import json
import os
from datetime import date, timedelta

if os.environ.get("LANGSMITH_ENABLED", "true").lower() in ("1", "true", "yes"):
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = os.environ.get(
        "LANGSMITH_PROJECT", "Gym Workout Analysis"
    )

from langchain_groq import ChatGroq
from langsmith import traceable

from config import (
    LANGSMITH_ENABLED,
    LLM_ENABLED,
    LLM_MOCK,
    LLM_MODEL,
    LLM_PROVIDER,
    SIMILAR_SESSION_COUNT,
    TONE,
    WEEKLY_WINDOW_DAYS,
)
from log import info, warn

MUSCLE_GROUPS = {
    "chest": [
        "bench press",
        "incline bench",
        "decline bench",
        "chest press",
        "cable fly",
        "pec deck",
        "dumbbell fly",
        "push up",
        "chest dip",
        "incline dumbbell",
        "flat db",
        "cable standing fly",
    ],
    "triceps": [
        "tricep",
        "triceps",
        "pushdown",
        "overhead extension",
        "skull crusher",
        "close grip bench",
        "tricep dip",
    ],
    "back": [
        "lat pulldown",
        "pull up",
        "barbell row",
        "dumbbell row",
        "cable row",
        "seated row",
        "pullover",
        "deadlift",
        "chin up",
        "single-arm cable row",
        "wide-grip cable row",
        "cable lat pullover",
    ],
    "biceps": [
        "bicep",
        "biceps",
        "curl",
        "hammer curl",
        "preacher curl",
        "incline curl",
        "concentration curl",
        "reverse curl",
    ],
    "shoulders": [
        "shoulder press",
        "overhead press",
        "lateral raise",
        "front raise",
        "rear delt",
        "face pull",
        "upright row",
        "seated db shoulder",
        "cable lateral raise",
    ],
    "legs": [
        "squat",
        "leg press",
        "lunge",
        "leg extension",
        "leg curl",
        "calf raise",
        "romanian deadlift",
        "bulgarian split",
        "smith squat",
        "walking lunge",
        "seated leg curl",
        "standing calf",
    ],
    "core": [
        "plank",
        "crunch",
        "sit up",
        "leg raise",
        "cable crunch",
        "ab wheel",
        "russian twist",
        "hanging leg raise",
        "woodchop",
        "decline crunch",
    ],
}


def analyze_workout(
    today_workout: dict, history_pool: list | None = None, tone: str | None = None
) -> dict:
    effective_tone = tone or TONE
    if LLM_ENABLED and not LLM_MOCK:
        return _analyze_with_llm(today_workout, history_pool, effective_tone)
    else:
        info(f"{LLM_PROVIDER.upper()}: Using mock response")
        return mock_response(today_workout, history_pool)


def _analyze_with_llm(
    today_workout: dict, history_pool: list | None = None, tone: str = "balanced"
) -> dict:
    llm = ChatGroq(
        model=LLM_MODEL,
        groq_api_key=get_api_key(),
    )

    prompt = build_prompt(today_workout, history_pool, tone)

    try:
        if LANGSMITH_ENABLED:
            raw = _analyze_with_tracing(llm, prompt)
        else:
            response = llm.invoke(prompt)
            raw = response.content

        parsed = _parse_response(raw)
        return _validate_and_correct(parsed, today_workout, history_pool)
    except Exception as e:
        warn(f"LLM API call failed: {e}")
        raise


@traceable(name="gym_workout_analysis")
def _analyze_with_tracing(llm, prompt: str):
    return llm.invoke(prompt).content


def _parse_response(raw: str) -> dict:
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned)
    except json.JSONDecodeError:
        warn("Failed to parse LLM JSON, returning raw text")
        return {"raw_text": raw}


def _validate_and_correct(
    analysis: dict, today_workout: dict, history_pool: list | None
) -> dict:
    """Check known-verifiable fields against the same precomputed facts the
    prompt was built from, and override them if the LLM drifted.

    Deliberately NOT a second LLM call: an 8B model checking its own numeric
    claims has the same reasoning gap that produced the claims in the first
    place. Only fields we can check deterministically are touched here.
    """
    if "raw_text" in analysis:
        return analysis

    history_pool = history_pool or []
    similar = _select_similar_sessions(today_workout, history_pool)
    recent_window = _filter_recent_window(history_pool)

    progression = analysis.get("progression")
    if not similar and isinstance(progression, str) and "no baseline yet" not in progression.lower():
        analysis["progression"] = "No baseline yet."

    if recent_window:
        all_volumes: dict[str, float] = {}
        for h in recent_window:
            h_groups = _categorize_exercises(h)
            h_stats = _compute_stats(h)
            for g in h_groups:
                all_volumes[g] = all_volumes.get(g, 0) + h_stats["muscle_volumes"].get(
                    g, 0
                )
        most_trained, least_trained = _identify_volume_extremes(all_volumes)

        vd = analysis.get("volume_distribution")
        if most_trained and least_trained and isinstance(vd, str):
            vd_lower = vd.lower()
            if most_trained not in vd_lower or least_trained not in vd_lower:
                analysis["volume_distribution"] = (
                    f"{most_trained.capitalize()} is the most-trained and "
                    f"{least_trained.capitalize()} is the least-trained "
                    "muscle group this week."
                )

    return analysis


def _match_muscle_group(name_lower: str) -> str | None:
    """Best muscle-group match for an exercise name, picking the longest
    (most specific) matching keyword across ALL groups rather than the
    first group that matches anything. Without this, a generic keyword
    like "curl" (biceps) would shadow a more specific one like "leg curl"
    (legs) just because biceps is checked first.
    """
    best_group = None
    best_len = 0
    for group, keywords in MUSCLE_GROUPS.items():
        for kw in keywords:
            if len(kw) > best_len and kw in name_lower:
                best_group = group
                best_len = len(kw)
    return best_group


def _categorize_exercises(workout: dict) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {g: [] for g in MUSCLE_GROUPS}

    desc = workout.get("description", {})
    exercises = workout.get("exercises", None)

    exercise_names = []
    if exercises:
        exercise_names = [ex.get("excercise_name", "") for ex in exercises]
    elif desc:
        exercise_names = list(desc.keys())

    for name in exercise_names:
        group = _match_muscle_group(name.lower())
        if group is not None:
            groups[group].append(name)
        else:
            groups.setdefault("other", []).append(name)

    return {k: v for k, v in groups.items() if v}


def _compute_stats(workout: dict) -> dict:
    desc = workout.get("description", {})
    exercises = workout.get("exercises", None)

    total_volume = 0
    top_set_weight = 0
    total_sets = 0
    muscle_volumes: dict[str, float] = {}

    if exercises:
        for ex in exercises:
            name = ex.get("excercise_name", "")
            for s in ex.get("sets", []):
                w = float(s.get("weight", 0))
                r = int(s.get("reps", 0))
                vol = w * r
                total_volume += vol
                total_sets += 1
                if w > top_set_weight:
                    top_set_weight = w
                group = _match_muscle_group(name.lower())
                if group is not None:
                    muscle_volumes[group] = muscle_volumes.get(group, 0) + vol
    elif desc:
        for ex_name, sets in desc.items():
            for s in sets:
                w = float(s.get("weight_kg", 0))
                r = int(s.get("reps", 0))
                vol = w * r
                total_volume += vol
                total_sets += 1
                if w > top_set_weight:
                    top_set_weight = w
                group = _match_muscle_group(ex_name.lower())
                if group is not None:
                    muscle_volumes[group] = muscle_volumes.get(group, 0) + vol

    return {
        "total_volume": total_volume,
        "top_set_weight": top_set_weight,
        "total_sets": total_sets,
        "muscle_volumes": muscle_volumes,
    }


def _detect_fatigue(history: list) -> list[str]:
    if len(history) < 3:
        return []

    warnings = []
    volumes = [h.get("total_volume", 0) for h in history]
    top_sets = []
    for h in history:
        desc = h.get("description", {})
        exercises = h.get("exercises", None)
        max_w = 0
        if exercises:
            for ex in exercises:
                for s in ex.get("sets", []):
                    max_w = max(max_w, float(s.get("weight", 0)))
        elif desc:
            for ex_name, sets in desc.items():
                for s in sets:
                    max_w = max(max_w, float(s.get("weight_kg", 0)))
        top_sets.append(max_w)

    if len(volumes) >= 3:
        recent = volumes[-3:]
        if recent[-1] < recent[-2] < recent[-3]:
            pct_drop = (
                ((recent[-2] - recent[-1]) / recent[-2]) * 100 if recent[-2] > 0 else 0
            )
            warnings.append(f"Volume dropped {pct_drop:.0f}% last 2 sessions")

    if len(top_sets) >= 3:
        recent_ts = top_sets[-3:]
        if recent_ts[-1] < recent_ts[-2] < recent_ts[-3]:
            warnings.append("Top set weight declining for 2+ sessions")

    return warnings


def _compute_volume_distribution(muscle_volumes: dict[str, float]) -> dict[str, str]:
    if not muscle_volumes:
        return {}

    total = sum(muscle_volumes.values())
    if total == 0:
        return {}

    dist = {}
    for group, vol in muscle_volumes.items():
        pct = (vol / total) * 100
        dist[group] = f"{pct:.0f}%"

    return dist


def _identify_volume_extremes(
    muscle_volumes: dict[str, float],
) -> tuple[str | None, str | None]:
    """Most- and least-trained muscle group by volume share this window,
    excluding the catch-all "other" bucket. Computed here rather than left
    to the LLM: small models are unreliable at picking argmin/argmax over
    several percentages shown as text.
    """
    real = {g: v for g, v in muscle_volumes.items() if g != "other"}
    if len(real) < 2:
        return None, None
    most = max(real.items(), key=lambda kv: kv[1])[0]
    least = min(real.items(), key=lambda kv: kv[1])[0]
    if most == least:
        return None, None
    return most, least


def _dominant_muscle_group(workout: dict) -> str | None:
    """Highest-volume muscle group for this workout, or None if nothing matched.

    Ties resolve to whichever group's exercise appears first in the workout
    (insertion order into the per-workout muscle-volume tally) - deterministic
    but not otherwise meaningful.
    """
    muscle_volumes = _compute_stats(workout)["muscle_volumes"]
    if not muscle_volumes:
        return None
    return max(muscle_volumes.items(), key=lambda kv: kv[1])[0]


def _workout_date(workout: dict) -> date | None:
    raw = workout.get("date") or workout.get("workout_perform_date")
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def _select_similar_sessions(
    today_workout: dict, history: list[dict], limit: int = SIMILAR_SESSION_COUNT
) -> list[dict]:
    """Past sessions sharing today's dominant muscle group, most recent
    `limit`, in chronological order (oldest first) so trend logic like
    _detect_fatigue keeps working unmodified."""
    today_group = _dominant_muscle_group(today_workout)
    if today_group is None:
        return []

    matches = [h for h in history if _dominant_muscle_group(h) == today_group]
    matches.sort(key=lambda h: _workout_date(h) or date.min)
    return matches[-limit:]


def _filter_recent_window(
    history: list[dict], window_days: int = WEEKLY_WINDOW_DAYS
) -> list[dict]:
    """All workouts within window_days of today, any type, chronological order."""
    cutoff = date.today() - timedelta(days=window_days)
    recent = [h for h in history if (_workout_date(h) or date.min) >= cutoff]
    recent.sort(key=lambda h: _workout_date(h) or date.min)
    return recent


def get_api_key() -> str:
    provider = LLM_PROVIDER.lower()
    if provider == "groq":
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY not set")
        return key
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def _format_workout(workout: dict) -> str:
    lines = []
    lines.append(
        f"Date: {workout.get('workout_perform_date', workout.get('date', 'N/A'))}"
    )
    lines.append(f"Title: {workout.get('title', 'N/A')}")
    lines.append(f"Total Volume: {workout.get('total_volume', 'N/A')} kg")

    desc = workout.get("description", {})
    exercises = workout.get("exercises", None)

    if exercises:
        for ex in exercises:
            name = ex.get("excercise_name", "Unknown")
            sets = ex.get("sets", [])
            lines.append(f"  {name}:")
            for i, s in enumerate(sets, 1):
                w = s.get("weight", s.get("weight_kg", "?"))
                r = s.get("reps", "?")
                lines.append(f"    Set {i}: {w} kg x {r}")
    elif desc:
        for ex_name, sets in desc.items():
            lines.append(f"  {ex_name}:")
            for i, s in enumerate(sets, 1):
                w = s.get("weight_kg", s.get("weight", "?"))
                r = s.get("reps", "?")
                lines.append(f"    Set {i}: {w} kg x {r}")

    return "\n".join(lines)


def _format_history(history: list) -> str:
    return "\n\n".join(_format_workout(h) for h in history)


def build_prompt(
    today_workout: dict, history_pool: list | None = None, tone: str = "balanced"
) -> str:
    today_group = _dominant_muscle_group(today_workout)
    similar = _select_similar_sessions(today_workout, history_pool or [])
    recent_window = _filter_recent_window(history_pool or [])

    if not similar:
        similar_text = "No prior sessions with a matching dominant muscle group yet."
    else:
        similar_text = _format_history(similar)

    if not recent_window:
        recent_text = "No other workouts recorded in this window."
    else:
        recent_text = _format_history(recent_window)

    today_text = _format_workout(today_workout)

    today_groups = _categorize_exercises(today_workout)

    fatigue_warnings = []
    volume_dist = {}
    history_stats_summary = ""
    if len(similar) >= 2:
        fatigue_warnings = _detect_fatigue(similar)
        history_stats_summary = f"Historical avg volume ({today_group or 'similar'} sessions): {sum(h.get('total_volume', 0) for h in similar) / len(similar):.0f} kg"
    elif len(similar) == 1:
        history_stats_summary = "Only 1 similar session in history. No trend data."

    most_trained, least_trained = None, None
    if recent_window:
        all_volumes: dict[str, float] = {}
        for h in recent_window:
            h_groups = _categorize_exercises(h)
            h_stats = _compute_stats(h)
            for g in h_groups:
                all_volumes[g] = all_volumes.get(g, 0) + h_stats["muscle_volumes"].get(
                    g, 0
                )
        volume_dist = _compute_volume_distribution(all_volumes)
        most_trained, least_trained = _identify_volume_extremes(all_volumes)

    tone_instruction = {
        "harsh": "Be brutally honest. Call out weak points directly. No sugarcoating. Push the user to do better.",
        "balanced": "Be direct but constructive. Acknowledge wins, but don't hesitate to point out issues.",
    }.get(
        tone,
        "Be direct but constructive. Acknowledge wins, but don't hesitate to point out issues.",
    )

    exercise_coverage_text = ""
    if today_groups:
        lines = []
        for group, exs in today_groups.items():
            lines.append(f"  {group}: {', '.join(exs)}")
        exercise_coverage_text = "\n".join(lines)

    fatigue_text = ""
    if fatigue_warnings:
        fatigue_text = "\n".join(f"  - {w}" for w in fatigue_warnings)
    else:
        fatigue_text = "  None detected."

    volume_dist_text = ""
    if volume_dist:
        volume_dist_text = "\n".join(f"  {g}: {p}" for g, p in volume_dist.items())
    else:
        volume_dist_text = "  Insufficient data."

    if most_trained and least_trained:
        imbalance_text = (
            f"Most trained this week: {most_trained}. "
            f"Least trained this week: {least_trained}."
        )
    else:
        imbalance_text = "Not enough distinct muscle groups trained this week to compare."

    return f"""You are a strength training and hypertrophy coach. Analyze the user's gym workout.

TONE: {tone_instruction}

RULES:
- Reps decreasing on heavier sets within a session is NORMAL — the user goes to failure on final sets intentionally. Do NOT flag this as an issue.
- Only flag issues when comparing ACROSS sessions (today vs history), not within a single session.
- Only flag issues if the data clearly supports it. Do not invent problems.
- NEVER compare total volume or top set weight across DIFFERENT muscle groups (e.g. today's chest volume vs. a shoulder day's volume, or a squat's top set vs. a lateral raise's top set). Isolation movements (shoulders, arms, core) inherently use far lower absolute weight than compound movements (chest, back, legs) due to leverage, not training quality — this comparison is always invalid and must never appear in your response. Only compare volume/weight within the SAME muscle group.
- RECENT TRAINING WINDOW is for weekly muscle-group coverage context only (what got trained, how often) — use the pre-computed Volume distribution percentages for balance commentary, not raw numbers pulled from individual sessions in that window.
- Do not state a specific percentage or kg figure anywhere in your response unless it appears verbatim in the data above. If you're unsure of an exact number, describe the trend in words (e.g. "increased", "underrepresented") instead of inventing a figure.
- Response MUST be under 1600 characters.

PRE-COMPUTED DATA:
Exercise coverage today:
{exercise_coverage_text}

Fatigue signals (from history):
{fatigue_text}

Volume distribution (last {WEEKLY_WINDOW_DAYS} days, all workout types):
{volume_dist_text}
{imbalance_text}

{history_stats_summary}

TODAY'S WORKOUT:
{today_text}

SIMILAR PAST SESSIONS ({today_group or "unmatched"}, last {len(similar)}):
{similar_text}

RECENT TRAINING WINDOW (last {WEEKLY_WINDOW_DAYS} days, all workout types):
{recent_text}

Respond in EXACTLY this JSON format, nothing else:
{{
  "progression": "Compare today ONLY to the sessions in SIMILAR PAST SESSIONS (same primary muscle group): volume trend, top set weight, failure quality. If no similar sessions, say 'No baseline yet.'",
  "coverage": "Note any missing muscle groups or exercises that seem absent based on the workout type.",
  "fatigue": "Summarize fatigue signals (from SIMILAR PAST SESSIONS) or say 'None detected.'",
  "volume_distribution": "State in your own words that {most_trained or 'N/A'} is the most-trained and {least_trained or 'N/A'} is the least-trained muscle group this week (these are given above as 'Most/Least trained this week' - use them exactly as given, do not compute this yourself). Do not state or invent any percentage or kg number in this field.",
  "positives": ["1-2 specific positives from the data"],
  "improvements": ["1-2 specific issues, only if backed by data. Empty list if none."],
  "next_session": "One concrete, actionable cue."
}}"""


def mock_response(today_workout: dict, history_pool: list | None = None) -> dict:
    return {
        "progression": "Volume is stable across recent similar sessions.",
        "coverage": "Exercise selection covers the main movement patterns.",
        "fatigue": "None detected.",
        "volume_distribution": "Distribution looks balanced.",
        "positives": ["Consistent training frequency"],
        "improvements": [],
        "next_session": "Consider adding one additional back movement next session.",
    }

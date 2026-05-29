import json
import os

if os.environ.get("LANGSMITH_ENABLED", "true").lower() in ("1", "true", "yes"):
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_PROJECT"] = os.environ.get("LANGSMITH_PROJECT", "Gym Workout Analysis")

from langchain_groq import ChatGroq
from langsmith import traceable

from config import LANGSMITH_ENABLED, LLM_ENABLED, LLM_MOCK, LLM_MODEL, LLM_PROVIDER, TONE
from log import info, warn

MUSCLE_GROUPS = {
    "chest": [
        "bench press", "incline bench", "decline bench", "chest press",
        "cable fly", "pec deck", "dumbbell fly", "push up", "chest dip",
        "incline dumbbell", "flat db", "cable standing fly",
    ],
    "triceps": [
        "tricep", "triceps", "pushdown", "overhead extension",
        "skull crusher", "close grip bench", "tricep dip",
    ],
    "back": [
        "lat pulldown", "pull up", "barbell row", "dumbbell row",
        "cable row", "seated row", "pullover", "deadlift",
        "chin up", "single-arm cable row", "wide-grip cable row",
        "cable lat pullover",
    ],
    "biceps": [
        "bicep", "biceps", "curl", "hammer curl", "preacher curl",
        "incline curl", "concentration curl", "reverse curl",
    ],
    "shoulders": [
        "shoulder press", "overhead press", "lateral raise",
        "front raise", "rear delt", "face pull", "upright row",
        "seated db shoulder", "cable lateral raise",
    ],
    "legs": [
        "squat", "leg press", "lunge", "leg extension", "leg curl",
        "calf raise", "romanian deadlift", "bulgarian split",
        "smith squat", "walking lunge", "seated leg curl",
        "standing calf",
    ],
}


def analyze_workout(today_workout: dict, history_28_days: list | None = None, tone: str | None = None) -> dict:
    effective_tone = tone or TONE
    if LLM_ENABLED and not LLM_MOCK:
        return _analyze_with_llm(today_workout, history_28_days, effective_tone)
    else:
        info(f"{LLM_PROVIDER.upper()}: Using mock response")
        return mock_response(today_workout, history_28_days)


def _analyze_with_llm(today_workout: dict, history_28_days: list | None = None, tone: str = "balanced") -> dict:
    llm = ChatGroq(
        model=LLM_MODEL,
        groq_api_key=get_api_key(),
    )

    prompt = build_prompt(today_workout, history_28_days, tone)

    try:
        if LANGSMITH_ENABLED:
            raw = _analyze_with_tracing(llm, prompt)
        else:
            response = llm.invoke(prompt)
            raw = response.content

        return _parse_response(raw)
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
        warn(f"Failed to parse LLM JSON, returning raw text")
        return {"raw_text": raw}


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
        name_lower = name.lower()
        matched = False
        for group, keywords in MUSCLE_GROUPS.items():
            if any(kw in name_lower for kw in keywords):
                groups[group].append(name)
                matched = True
                break
        if not matched:
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
                for group, keywords in MUSCLE_GROUPS.items():
                    if any(kw in name.lower() for kw in keywords):
                        muscle_volumes[group] = muscle_volumes.get(group, 0) + vol
                        break
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
                for group, keywords in MUSCLE_GROUPS.items():
                    if any(kw in ex_name.lower() for kw in keywords):
                        muscle_volumes[group] = muscle_volumes.get(group, 0) + vol
                        break

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
            pct_drop = ((recent[-2] - recent[-1]) / recent[-2]) * 100 if recent[-2] > 0 else 0
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
    lines.append(f"Date: {workout.get('workout_perform_date', workout.get('date', 'N/A'))}")
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


def build_prompt(today_workout: dict, history_28_days: list | None = None, tone: str = "balanced") -> str:
    if not history_28_days:
        history_text = "No prior workouts in the last 4 weeks."
    elif len(history_28_days) == 1:
        history_text = "Only today's workout available. No prior workout history to compare against."
    else:
        history_text = _format_history(history_28_days)

    today_text = _format_workout(today_workout)

    today_stats = _compute_stats(today_workout)
    today_groups = _categorize_exercises(today_workout)

    fatigue_warnings = []
    volume_dist = {}
    history_stats_summary = ""
    if history_28_days and len(history_28_days) >= 2:
        fatigue_warnings = _detect_fatigue(history_28_days)
        latest_groups = _categorize_exercises(history_28_days[-1])
        all_volumes: dict[str, float] = {}
        for h in history_28_days:
            h_groups = _categorize_exercises(h)
            h_stats = _compute_stats(h)
            for g in h_groups:
                all_volumes[g] = all_volumes.get(g, 0) + h_stats["muscle_volumes"].get(g, 0)
        volume_dist = _compute_volume_distribution(all_volumes)
        history_stats_summary = f"Historical avg volume: {sum(h.get('total_volume', 0) for h in history_28_days) / len(history_28_days):.0f} kg"
    elif history_28_days and len(history_28_days) == 1:
        history_stats_summary = "Only 1 session in history. No trend data."

    tone_instruction = {
        "harsh": "Be brutally honest. Call out weak points directly. No sugarcoating. Push the user to do better.",
        "balanced": "Be direct but constructive. Acknowledge wins, but don't hesitate to point out issues.",
    }.get(tone, "Be direct but constructive. Acknowledge wins, but don't hesitate to point out issues.")

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

    return f"""You are a strength training and hypertrophy coach. Analyze the user's gym workout.

TONE: {tone_instruction}

RULES:
- Reps decreasing on heavier sets within a session is NORMAL — the user goes to failure on final sets intentionally. Do NOT flag this as an issue.
- Only flag issues when comparing ACROSS sessions (today vs history), not within a single session.
- Only flag issues if the data clearly supports it. Do not invent problems.
- Response MUST be under 1600 characters.

PRE-COMPUTED DATA:
Exercise coverage today:
{exercise_coverage_text}

Fatigue signals (from history):
{fatigue_text}

Volume distribution (last 4 weeks):
{volume_dist_text}

{history_stats_summary}

TODAY'S WORKOUT:
{today_text}

PREVIOUS 4 WEEKS:
{history_text}

Respond in EXACTLY this JSON format, nothing else:
{{
  "progression": "Compare today to history: volume trend, top set weight, failure quality. If no history, say 'No baseline yet.'",
  "coverage": "Note any missing muscle groups or exercises that seem absent based on the workout type.",
  "fatigue": "Summarize fatigue signals or say 'None detected.'",
  "volume_distribution": "Note if any muscle group is over/underrepresented.",
  "positives": ["1-2 specific positives from the data"],
  "improvements": ["1-2 specific issues, only if backed by data. Empty list if none."],
  "next_session": "One concrete, actionable cue."
}}"""


def mock_response(today_workout: dict, history_28_days: list | None = None) -> dict:
    return {
        "progression": "Volume is stable over the last 4 weeks.",
        "coverage": "Exercise selection covers the main movement patterns.",
        "fatigue": "None detected.",
        "volume_distribution": "Distribution looks balanced.",
        "positives": ["Consistent training frequency"],
        "improvements": [],
        "next_session": "Consider adding one additional back movement next session.",
    }

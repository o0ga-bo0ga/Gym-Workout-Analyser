import os
from typing import Any

from config import GEMINI_MODE
from log import info

NO_HISTORY_MESSAGE = "No workout history available for the last 4 weeks."


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def _load_workout_plan() -> str:
    """Load the workout plan from external file."""
    plan_path = os.path.join(os.path.dirname(__file__), "workout_plan.txt")
    try:
        with open(plan_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No workout plan configured."


def format_workout_for_llm(workout: dict[str, Any]) -> str:
    """
    Format a single workout into a clean, human-readable string for LLM consumption.
    """
    title = workout.get("title", "Unknown Workout")
    date = workout.get("workout_perform_date", "")[:10]
    total_volume = workout.get("total_volume", 0)
    exercises = workout.get("exercises", [])
    
    # Calculate totals
    total_sets = sum(len(ex.get("sets", [])) for ex in exercises)
    
    lines = [
        f"📅 WORKOUT: {title}",
        f"Date: {date}",
        f"Total Volume: {total_volume:,} kg | {len(exercises)} exercises | {total_sets} sets",
        "",
        "EXERCISES:"
    ]
    
    for i, ex in enumerate(exercises, 1):
        name = ex.get("excercise_name", "Unknown Exercise")
        lines.append(f"\n{i}. {name}")
        
        for j, s in enumerate(ex.get("sets", []), 1):
            weight = _to_float(s.get("weight", 0))
            reps = _to_int(s.get("reps", 0))
            
            lines.append(f"   Set {j}: {weight:.1f}kg × {reps} reps")
    
    return "\n".join(lines)


def format_history_for_llm(history: list[dict[str, Any]]) -> str:
    """
    Format workout history with full exercise details for LLM consumption.
    """
    if not history:
        return NO_HISTORY_MESSAGE
    
    lines = ["📊 WORKOUT HISTORY (Last 4 Weeks):"]
    
    for w in history:
        date = w.get("date", "")[:10]
        title = w.get("title", "Unknown")
        volume = w.get("total_volume", 0)
        exercise_count = w.get("exercise_count", 0)
        set_count = w.get("set_count", 0)
        description = w.get("description", {})
        
        lines.extend([
            "",
            f"─── {date}: {title} ───",
            f"Volume: {volume:,} kg | {exercise_count} exercises | {set_count} sets",
        ])
        
        # Add exercise details from description
        if description and isinstance(description, dict):
            for i, (exercise_name, sets) in enumerate(description.items(), 1):
                lines.append(f"  {i}. {exercise_name}")
                if isinstance(sets, list):
                    for j, s in enumerate(sets, 1):
                        weight = _to_float(s.get("weight_kg", 0))
                        reps = _to_int(s.get("reps", 0))
                        lines.append(f"     Set {j}: {weight:.1f}kg × {reps} reps")
    
    # Add summary stats
    total_workouts = len(history)
    total_volume = sum(w.get("total_volume", 0) for w in history)
    avg_volume = total_volume // total_workouts if total_workouts > 0 else 0
    
    lines.extend([
        "",
        "─── SUMMARY ───",
        f"{total_workouts} workouts | Total volume: {total_volume:,} kg | Avg per session: {avg_volume:,} kg"
    ])
    
    return "\n".join(lines)


def analyze_workout(today_workout: dict[str, Any], history: list[dict[str, Any]]) -> str:
    """Analyze today's workout using Gemini LLM."""
    if not GEMINI_MODE:
        info("GEMINI: Using mock response")
        return mock_response(today_workout, history)

    from google import genai

    client = genai.Client()  # API key from env

    prompt = build_prompt(today_workout, history)

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    return response.text


def build_prompt(today_workout: dict[str, Any], history: list[dict[str, Any]]) -> str:
    """Build the analysis prompt for Gemini."""
    workout_plan = _load_workout_plan()
    
    # Format data for LLM
    today_formatted = format_workout_for_llm(today_workout)
    history_formatted = format_history_for_llm(history)

    return f"""You are a strength training and hypertrophy coach. Following is my workout plan:

{workout_plan}

Analyze today's workout in the context of the past 4 weeks workout data provided.

Constraints:
- Be concise and practical
- No motivational fluff
- No disclaimers
- Days not listed in the history should be treated as rest days.
- If you see any weird rep ranges, just know that I tried going to failure, because thats what I'm gonna do regardless of weight chosen, I'm gonna pursue failure on the end sets
- Every workout will have the muscle worked in the title, that is, it will have upper, lower/legs, chest tri, back bi, arms shoulder, in the title. please look at that, see which workout i did and then analyse.
- Keep the response under 1800 characters. This is very important as if it exceeds 2000 characters the discord messaging will fail.

---

{today_formatted}

---

{history_formatted}

---

Cover:
1. Relevance to the workout plan
2. Progression quality
3. Good things about this workout, if none say so
4. Bad things about this workout if none say so
5. One concrete recommendation for the next session
"""


def mock_response(today_workout: dict[str, Any], history: list[dict[str, Any]]) -> str:
    """Return a mock response for testing."""
    return """- Volume is stable over the last 4 weeks
- Exercise selection is balanced but pressing dominates
- No clear fatigue signals detected
- Load progression appears consistent
- Consider adding one additional back movement next session"""

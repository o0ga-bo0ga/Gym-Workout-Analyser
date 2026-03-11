from typing import Any

from workout_utils import get_exercise_name, parse_weight_reps


def build_workout_description(workout: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """
    Convert Lyfta workout JSON into a compact, domain-specific structure.
    """
    description: dict[str, list[dict[str, Any]]] = {}

    for ex in workout.get("exercises", []):
        name = get_exercise_name(ex)
        if not name:
            continue

        sets_data: list[dict[str, Any]] = []
        for s in ex.get("sets", []):
            parsed = parse_weight_reps(s)
            if parsed is None:
                continue
            weight, reps = parsed

            sets_data.append({
                "weight_kg": weight,
                "reps": reps,
            })

        if sets_data:
            description[name] = sets_data

    return description

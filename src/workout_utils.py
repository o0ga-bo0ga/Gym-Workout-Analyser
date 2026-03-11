from typing import Any


def get_exercise_name(exercise: dict[str, Any]) -> str | None:
    return (
        exercise.get("excercise_name")
        or exercise.get("exercise_name")
        or exercise.get("name")
    )


def parse_weight_reps(set_data: dict[str, Any]) -> tuple[float, int] | None:
    weight = set_data.get("weight")
    reps = set_data.get("reps")
    if weight is None or reps is None:
        return None

    try:
        return float(weight), int(reps)
    except (ValueError, TypeError):
        return None

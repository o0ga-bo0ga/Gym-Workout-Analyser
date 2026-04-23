def build_workout_description(workout):
    """
    Convert Lyfta workout JSON into a compact, domain-specific structure.
    """
    description = {}

    for ex in workout.get("exercises", []):
        name = ex.get("excercise_name")
        if not name:
            continue

        sets_data = []
        for s in ex.get("sets", []):
            weight = s.get("weight")
            reps = s.get("reps")

            if weight is None or reps is None:
                continue

            sets_data.append({
                "weight_kg": float(weight),
                "reps": int(reps)
            })

        if sets_data:
            description[name] = sets_data

    return description

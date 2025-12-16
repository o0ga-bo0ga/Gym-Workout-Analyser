def format_workout(workout):
    if workout is None:
        return "Rest Day\n\nNo workout logged today."

    date_time = workout["workout_perform_date"]
    date = date_time.split(" ")[0]
    day = date_time.split(" ")[0]  # keep simple, LLM can infer day

    lines = []
    lines.append(f"Date: {date}")
    lines.append(f"Day: {day}")
    lines.append("")
    lines.append("Workout:")

    for ex in workout.get("exercises", []):
        lines.append(f"- {ex['excercise_name']}")
        for idx, s in enumerate(ex.get("sets", []), start=1):
            lines.append(
                f"  Set {idx}: {s['weight']}kg x {s['reps']} reps"
            )

    return "\n".join(lines)

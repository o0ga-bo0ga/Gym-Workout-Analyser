def format_workout(workout):
    date_time = workout["workout_perform_date"]
    date = date_time.split(" ")[0]
    day = workout.get("day", "")  # optional if you already inject it earlier

    lines = []
    lines.append(f"Date: {date}")
    if day:
        lines.append(f"Day: {day}")
    lines.append("")

    for ex in workout["exercises"]:
        lines.append(f"- {ex['excercise_name']}")
        for s in ex["sets"]:
            weight = s["weight"]
            reps = s["reps"]
            lines.append(f"  • {weight} kg × {reps}")
        lines.append("")

    return date, day, "\n".join(lines)

from database import fetch_workout_summary
from log import info


def summarize_last_21_days():
    summary = fetch_workout_summary(days=21)

    info("ANALYSIS_PREP: Last 21 days summary")
    info(f"  total_days: {summary.total_days}")
    info(f"  workout_days: {summary.workout_days}")
    info(f"  rest_days: {summary.rest_days}")
    info(f"  total_volume: {summary.total_volume}")
    info(f"  avg_volume: {summary.avg_volume}")
    info(f"  avg_exercises: {summary.avg_exercises}")
    info(f"  avg_sets: {summary.avg_sets}")

    return {
        "total_days": summary.total_days,
        "workout_days": summary.workout_days,
        "rest_days": summary.rest_days,
        "total_volume": summary.total_volume,
        "avg_volume": summary.avg_volume,
        "avg_exercises": summary.avg_exercises,
        "avg_sets": summary.avg_sets,
    }

import os

from analysis_prep import summarize_last_21_days
from config import ANALYSIS_ENABLED, DATABASE_ENABLED, DRY_RUN, LYFTA_ENABLED
from data_fetch import fetch_today_workout
from database import fetch_recent_workouts
from discord_client import format_discord_message, send_discord_message
from gemini_client import analyze_workout
from log import error, info, warn
from models import Workout
from persistence import persist_today_workout

REST_DAY_MESSAGE: str = os.environ.get("REST_DAY_MESSAGE", "Rest day taken. Recovery is important!")


def main() -> None:
    info("=== Daily Workout Pipeline Start ===")

    workout: Workout | None = None

    if LYFTA_ENABLED:
        workout = fetch_today_workout()
    else:
        warn("LYFTA disabled, skipping fetch")

    if DATABASE_ENABLED:
        try:
            persist_today_workout(workout)
        except Exception as e:
            error(f"Database failure: {e}")
            raise
    else:
        warn("Database disabled, skipping persistence")

    if workout is None:
        try:
            send_discord_message(REST_DAY_MESSAGE)
            info("Rest day reported")
        except Exception as e:
            warn(f"Rest day Discord send failed: {e}")
    elif ANALYSIS_ENABLED:
        try:
            history_28_days = fetch_recent_workouts(days=28)
            summary_21_days = summarize_last_21_days()
            info(f"GEMINI: history workouts = {len(history_28_days)}, summary = {summary_21_days.get('workout_days', 0)} workout days")

            analysis = analyze_workout(workout, history_28_days, summary_21_days)
            message = format_discord_message(analysis, workout)
            send_discord_message(message)
            info("Discord report sent")
            print(analysis)
        except Exception as e:
            warn(f"Analysis or Discord send failed: {e}")
            if not DRY_RUN:
                raise

    info("=== Pipeline Complete ===")


if __name__ == "__main__":
    main()

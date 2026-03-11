import os
from datetime import date
from typing import Any

from log import info, warn, error
from db import init_db, log_rest_day, log_workout, enforce_retention, fetch_recent_workouts
from lyfta import get_todays_workout
from gemini import analyze_workout
from config import LYFTA_ENABLED, DB_ENABLED, ANALYSIS_ENABLED, DRY_RUN
from discord import send_discord_message, format_discord_message

REST_DAY_MESSAGE = "Rest day logged. Recover well and hit the next session hard."
HISTORY_WINDOW_DAYS = 28


def fetch_today() -> dict[str, Any] | None:
    """Phase 1: Fetch today's workout from Lyfta API."""
    api_key = os.environ.get("LYFTA_API_KEY")
    if not api_key:
        raise RuntimeError("LYFTA_API_KEY not set")

    workout = get_todays_workout(api_key)

    if workout is None:
        info("PHASE1: Rest day detected")
        return None

    info("PHASE1: Workout detected")
    info(f"  Title: {workout.get('title')}")
    info(f"  Date: {workout.get('workout_perform_date')}")
    info(f"  Exercises: {len(workout.get('exercises', []))}")

    return workout


def persist_today(workout: dict[str, Any] | None) -> None:
    """Phase 2: Persist workout or rest day to database."""
    if DRY_RUN:
        info("DRY RUN: Skipping DB write")
        return

    init_db()
    today = date.today().isoformat()

    if workout is None:
        log_rest_day(today)
        info(f"PHASE2: Rest day logged for {today}")
    else:
        log_workout(workout)
        info(f"PHASE2: Workout logged for {today}")

    # Retention should never block ingestion
    try:
        enforce_retention(months=12)
        info("PHASE2: Retention enforced (12 months)")
    except Exception as e:
        info(f"PHASE2 WARNING: Retention failed: {e}")


def main() -> None:
    info("=== Daily Workout Pipeline Start ===")

    workout = None

    if LYFTA_ENABLED:
        workout = fetch_today()
    else:
        warn("LYFTA disabled, skipping fetch")

    if DB_ENABLED:
        try:
            persist_today(workout)
        except Exception as e:
            error(f"DB failure: {e}")
            raise
    else:
        warn("DB disabled, skipping persistence")

    if ANALYSIS_ENABLED and workout is not None:
        try:
            history = fetch_recent_workouts(days=HISTORY_WINDOW_DAYS)
            info(f"GEMINI TEST: history workouts = {len(history)}")
            analysis = analyze_workout(workout, history)
            message = format_discord_message(analysis, workout)
            send_discord_message(message)
            info("Discord report sent")
            print(analysis)
        except Exception as e:
            warn(f"Gemini analysis or Discord send failed: {e}")
    else:
        try:
            send_discord_message(REST_DAY_MESSAGE)
            info("Rest Day reported")
        except Exception as e:
            warn(f"Rest day Discord send failed: {e}")

    info("=== Pipeline Complete ===")


if __name__ == "__main__":
    main()

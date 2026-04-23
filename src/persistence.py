from datetime import date

from config import DRY_RUN
from database import (
    enforce_data_retention,
    initialize_database,
    save_rest_day,
    save_workout,
)
from log import info
from models import Workout


def persist_today_workout(workout: dict | None) -> Workout | None:
    if DRY_RUN:
        info("DRY RUN: Skipping DB write")
        return None

    initialize_database()
    today = date.today().isoformat()

    if workout is None:
        save_rest_day(today)
        info(f"PERSISTENCE: Rest day logged for {today}")
        return None

    saved_workout = save_workout(workout)
    info(f"PERSISTENCE: Workout logged for {today}: {saved_workout.title}")

    try:
        enforce_data_retention(months=12)
        info("PERSISTENCE: Retention enforced (12 months)")
    except Exception as e:
        info(f"PERSISTENCE WARNING: Retention failed: {e}")

    return saved_workout

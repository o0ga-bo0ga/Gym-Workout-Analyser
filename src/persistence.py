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
    return persist_workout_for_date(workout, date.today().isoformat())


def persist_workout_for_date(
    workout: dict | None, target_date: str
) -> Workout | None:
    if DRY_RUN:
        info("DRY RUN: Skipping DB write")
        return None

    initialize_database()

    if workout is None:
        save_rest_day(target_date)
        info(f"PERSISTENCE: Rest day logged for {target_date}")
        return None

    workout_for_save = dict(workout)
    workout_for_save["workout_perform_date"] = f"{target_date} 00:00:00"
    saved_workout = save_workout(workout_for_save)
    info(f"PERSISTENCE: Workout logged for {target_date}: {saved_workout.title}")

    try:
        enforce_data_retention(months=12)
        info("PERSISTENCE: Retention enforced (12 months)")
    except Exception as e:
        info(f"PERSISTENCE WARNING: Retention failed: {e}")

    return saved_workout

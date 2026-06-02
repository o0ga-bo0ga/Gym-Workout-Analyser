import os

from log import info
from lyfta_client import fetch_todays_workout, fetch_workout_for_date


def fetch_today_workout() -> dict | None:
    api_key = os.environ.get("LYFTA_API_KEY")
    if not api_key:
        raise RuntimeError("LYFTA_API_KEY not set")

    workout = fetch_todays_workout(api_key)

    if workout is None:
        info("DATA_FETCH: Rest day detected")
        return None

    info("DATA_FETCH: Workout detected")
    info(f"  Title: {workout.get('title')}")
    info(f"  Date: {workout.get('workout_perform_date')}")
    info(f"  Exercises: {len(workout.get('exercises', []))}")

    return workout


def fetch_workout_for_target_date(target_date: str) -> dict | None:
    api_key = os.environ.get("LYFTA_API_KEY")
    if not api_key:
        raise RuntimeError("LYFTA_API_KEY not set")

    workout = fetch_workout_for_date(api_key, target_date)

    if workout is None:
        info(f"DATA_FETCH: No workout in Lyfta for {target_date}")
        return None

    info(f"DATA_FETCH: Workout for {target_date} detected")
    info(f"  Title: {workout.get('title')}")
    info(f"  Date: {workout.get('workout_perform_date')}")
    info(f"  Exercises: {len(workout.get('exercises', []))}")

    return workout

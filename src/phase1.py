import os
from lyfta import get_todays_workout
from log import info

def fetch_today():
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

import os
from lyfta import get_todays_workout

def fetch_today():
    api_key = os.environ.get("LYFTA_API_KEY")
    if not api_key:
        raise RuntimeError("LYFTA_API_KEY not set")

    workout = get_todays_workout(api_key)

    if workout is None:
        print("PHASE1: Rest day detected")
        return None

    print("PHASE1: Workout detected")
    print(f"  Title: {workout.get('title')}")
    print(f"  Date: {workout.get('workout_perform_date')}")
    print(f"  Exercises: {len(workout.get('exercises', []))}")

    return workout

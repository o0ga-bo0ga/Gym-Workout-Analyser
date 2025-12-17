import os
from datetime import date
from lyfta import get_todays_workout
from db import init_db, log_rest_day, log_workout

def main():
    api_key = os.environ.get("LYFTA_API_KEY")
    if not api_key:
        raise RuntimeError("LYFTA_API_KEY not set")

    init_db()

    workout = get_todays_workout(api_key)
    today = date.today().isoformat()

    if workout is None:
        log_rest_day(today)
        print(f"PHASE2 RESULT: Rest day logged for {today}")
        return

    exercises = workout.get("exercises", [])
    set_count = sum(len(ex.get("sets", [])) for ex in exercises)

    print(f"PHASE2 RESULT: Workout detected for {today}")
    print(f"Title: {workout.get('title')}")
    print(f"Exercises: {len(exercises)}")
    print(f"Total sets: {set_count}")

    log_workout(workout)
    print("Workout persisted successfully")

if __name__ == "__main__":
    main()

import os
from lyfta import get_todays_workout

def main():
    api_key = os.environ.get("LYFTA_API_KEY")
    if not api_key:
        raise RuntimeError("LYFTA_API_KEY not set")

    workout = get_todays_workout(api_key)

    if workout is None:
        print("PHASE1 RESULT: Rest day (no workout logged today)")
        return

    title = workout.get("title", "Untitled")
    volume = workout.get("total_volume", "N/A")
    date = workout.get("workout_perform_date", "unknown")

    print("PHASE1 RESULT: Workout detected today")
    print(f"Title: {title}")
    print(f"Date: {date}")
    print(f"Total volume: {volume}")

if __name__ == "__main__":
    main()

import os
from lyfta import fetch_latest_workout
from formatter import format_workout
from database import init_db, save_workout, load_recent_workouts

def main():
    api_key = os.environ["LYFTA_API_KEY"]

    init_db()

    workout = fetch_latest_workout(api_key)
    formatted = format_workout(workout)

    if workout:
        workout_id = workout["id"]
        date = workout["workout_perform_date"].split(" ")[0]
        save_workout(workout_id, date, formatted)

    history = load_recent_workouts(limit=10)

    # For now just print (later feed to LLM)
    print("TODAY:\n", formatted)
    print("\nHISTORY:\n", history)

if __name__ == "__main__":
    main()

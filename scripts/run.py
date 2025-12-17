from fetch_workout import fetch_latest_workout
from format_workout import format_workout
from db import init_db, workout_exists, insert_workout

def main():
    init_db()

    workout = fetch_latest_workout()
    if workout is None:
        print("No workout found")
        return

    workout_id = workout["id"]

    if workout_exists(workout_id):
        print("Workout already processed, skipping")
        return

    date, day, content = format_workout(workout)

    insert_workout(workout_id, date, day, content)

    print("=== FORMATTED WORKOUT ===")
    print(content)

if __name__ == "__main__":
    main()

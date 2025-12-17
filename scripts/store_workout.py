import sqlite3
import os
import json

DB_PATH = "workouts.db"

# Example input file written by previous step
INPUT_JSON = "latest_workout.json"

def main():
    if not os.path.exists(INPUT_JSON):
        print("No workout input found. Exiting.")
        return

    with open(INPUT_JSON, "r") as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            date TEXT,
            day TEXT,
            content TEXT
        )
    """)

    workout_id = data.get("id")
    date = data.get("date")
    day = data.get("day")
    content = data.get("content")

    cur.execute("""
        INSERT OR REPLACE INTO workouts (id, date, day, content)
        VALUES (?, ?, ?, ?)
    """, (workout_id, date, day, content))

    conn.commit()
    conn.close()

    print("Workout stored successfully")

if __name__ == "__main__":
    main()

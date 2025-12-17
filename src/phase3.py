from datetime import date, timedelta
import sqlite3
from pathlib import Path

DB_PATH = Path("data/workouts.db")

def main():
    since = (date.today() - timedelta(days=21)).isoformat()

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # Total days recorded
    cur.execute("""
        SELECT COUNT(*)
        FROM workouts
        WHERE workout_date >= ?
    """, (since,))
    total_days = cur.fetchone()[0]

    # Workout days
    cur.execute("""
        SELECT COUNT(*)
        FROM workouts
        WHERE workout_date >= ?
        AND is_rest_day = 0
    """, (since,))
    workout_days = cur.fetchone()[0]

    # Rest days
    cur.execute("""
        SELECT COUNT(*)
        FROM workouts
        WHERE workout_date >= ?
        AND is_rest_day = 1
    """, (since,))
    rest_days = cur.fetchone()[0]

    # Volume + averages
    cur.execute("""
        SELECT
            SUM(total_volume),
            AVG(total_volume),
            AVG(exercise_count),
            AVG(set_count)
        FROM workouts
        WHERE workout_date >= ?
        AND is_rest_day = 0
    """, (since,))

    (
        total_volume,
        avg_volume,
        avg_exercises,
        avg_sets
    ) = cur.fetchone()

    con.close()

    print("PHASE3 RESULT: Last 21 days summary")
    print("----------------------------------")
    print(f"Total days tracked: {total_days}")
    print(f"Workout days: {workout_days}")
    print(f"Rest days: {rest_days}")
    print("")
    print(f"Total volume lifted: {total_volume}")
    print(f"Average volume per workout: {round(avg_volume, 2) if avg_volume else 0}")
    print(f"Average exercises per workout: {round(avg_exercises, 2) if avg_exercises else 0}")
    print(f"Average sets per workout: {round(avg_sets, 2) if avg_sets else 0}")

if __name__ == "__main__":
    main()

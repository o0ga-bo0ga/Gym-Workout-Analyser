from datetime import date, timedelta
import sqlite3
from pathlib import Path

DB_PATH = Path("data/workouts.db")

def summarize_last_21_days():
    since = (date.today() - timedelta(days=21)).isoformat()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        SELECT
            COUNT(*) AS total_days,
            SUM(CASE WHEN is_rest_day = 0 THEN 1 ELSE 0 END) AS workout_days,
            SUM(CASE WHEN is_rest_day = 1 THEN 1 ELSE 0 END) AS rest_days,
            SUM(total_volume),
            AVG(total_volume),
            AVG(exercise_count),
            AVG(set_count)
        FROM workouts
        WHERE workout_date >= ?
    """, (since,))

    (
        total_days,
        workout_days,
        rest_days,
        total_volume,
        avg_volume,
        avg_exercises,
        avg_sets
    ) = cur.fetchone()

    con.close()

    summary = {
        "total_days": total_days or 0,
        "workout_days": workout_days or 0,
        "rest_days": rest_days or 0,
        "total_volume": total_volume or 0,
        "avg_volume": round(avg_volume, 2) if avg_volume else 0,
        "avg_exercises": round(avg_exercises, 2) if avg_exercises else 0,
        "avg_sets": round(avg_sets, 2) if avg_sets else 0,
    }

    print("PHASE3: Last 21 days summary")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    return summary

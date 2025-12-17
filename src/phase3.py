import os
import psycopg2

def summarize_last_21_days():
    db_url = os.environ.get("SUPABASE_DATABASE_URL")
    if not db_url:
        raise RuntimeError("SUPABASE_DATABASE_URL not set")

    with psycopg2.connect(db_url, sslmode="require") as con:
        with con.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*) AS total_days,
                    SUM(CASE WHEN is_rest_day = FALSE THEN 1 ELSE 0 END) AS workout_days,
                    SUM(CASE WHEN is_rest_day = TRUE THEN 1 ELSE 0 END) AS rest_days,
                    COALESCE(SUM(total_volume), 0) AS total_volume,
                    COALESCE(AVG(total_volume), 0) AS avg_volume,
                    COALESCE(AVG(exercise_count), 0) AS avg_exercises,
                    COALESCE(AVG(set_count), 0) AS avg_sets
                FROM workouts
                WHERE workout_date >= CURRENT_DATE - INTERVAL '21 days';
            """)

            (
                total_days,
                workout_days,
                rest_days,
                total_volume,
                avg_volume,
                avg_exercises,
                avg_sets
            ) = cur.fetchone()

    summary = {
        "total_days": total_days,
        "workout_days": workout_days,
        "rest_days": rest_days,
        "total_volume": total_volume,
        "avg_volume": round(avg_volume, 2),
        "avg_exercises": round(avg_exercises, 2),
        "avg_sets": round(avg_sets, 2),
    }

    print("PHASE3: Last 21 days summary")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    return summary

import os
import json
import psycopg2
from psycopg2.extras import Json
from transform import build_workout_description

def get_connection():
    db_url = os.environ.get("SUPABASE_DATABASE_URL")
    if not db_url:
        raise RuntimeError("SUPABASE_DATABASE_URL not set")
    return psycopg2.connect(db_url, sslmode='require')

def init_db():
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                workout_date DATE PRIMARY KEY,
                workout_id INTEGER,
                title TEXT,
                total_volume INTEGER,
                exercise_count INTEGER,
                set_count INTEGER,
                raw_json JSONB,
                is_rest_day BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """)
        con.commit()

def log_rest_day(workout_date):
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute("""
            INSERT INTO workouts (workout_date, is_rest_day)
            VALUES (%s, TRUE)
            ON CONFLICT (workout_date) DO NOTHING;
            """, (workout_date,))
        con.commit()


def log_workout(workout):
    workout_date = workout["workout_perform_date"][:10]

    exercises = workout.get("exercises", [])
    exercise_count = len(exercises)
    set_count = sum(len(ex.get("sets", [])) for ex in exercises)

    description = build_workout_description(workout)

    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute("""
            INSERT INTO workouts (
                workout_date,
                workout_id,
                title,
                total_volume,
                exercise_count,
                set_count,
                description,
                is_rest_day
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
            ON CONFLICT (workout_date) DO NOTHING;
            """, (
                workout_date,
                workout.get("id"),
                workout.get("title"),
                workout.get("total_volume"),
                exercise_count,
                set_count,
                Json(description)
            ))
        con.commit()

def enforce_retention(months=12):
    """
    Delete workouts older than `months`.
    Safe to run multiple times.
    """
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute("""
                DELETE FROM workouts
                WHERE workout_date < CURRENT_DATE - INTERVAL %s;
            """, (f"{months} months",))
        con.commit()

def fetch_recent_workouts(days=28):
    """
    Returns recent workouts (excluding rest days),
    ordered from oldest -> newest.
    """
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute("""
                SELECT
                    workout_date,
                    title,
                    total_volume,
                    exercise_count,
                    set_count,
                    description
                FROM workouts
                WHERE
                    is_rest_day = FALSE
                    AND workout_date >= CURRENT_DATE - INTERVAL %s
                ORDER BY workout_date ASC;
            """, (f"{days} days",))
            rows = cur.fetchall()

    return [
        {
            "date": r[0].isoformat(),
            "title": r[1],
            "total_volume": r[2],
            "exercise_count": r[3],
            "set_count": r[4],
            "description": r[5],
        }
        for r in rows
    ]

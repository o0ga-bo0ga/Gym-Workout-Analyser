import atexit
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from psycopg2 import pool
from psycopg2.extras import Json

from models import Workout, WorkoutSummary
from workout_transformer import build_workout_description

_connection_pool: Optional[pool.ThreadedConnectionPool] = None
MIN_CONN = 1
MAX_CONN = 5


def _init_pool():
    global _connection_pool
    if _connection_pool is not None:
        return

    db_url = os.environ.get("SUPABASE_DATABASE_URL")
    if not db_url:
        raise RuntimeError("SUPABASE_DATABASE_URL not set")

    _connection_pool = pool.ThreadedConnectionPool(
        minconn=MIN_CONN, maxconn=MAX_CONN, dsn=db_url, sslmode="require"
    )
    atexit.register(_close_pool)


def _close_pool():
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None


@contextmanager
def _get_connection():
    if _connection_pool is None:
        _init_pool()
    con = _connection_pool.getconn()
    try:
        yield con
    finally:
        _connection_pool.putconn(con)


def get_connection():
    """Legacy function for backward compatibility."""
    return _get_connection()


def initialize_database():
    with _get_connection() as con:
        with con.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                workout_date DATE PRIMARY KEY,
                workout_id INTEGER,
                title TEXT,
                total_volume INTEGER,
                exercise_count INTEGER,
                set_count INTEGER,
                description JSONB,
                is_rest_day BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_workout_date ON workouts(workout_date);
            """)
        con.commit()


def save_rest_day(workout_date: str):
    with _get_connection() as con:
        with con.cursor() as cur:
            cur.execute(
                """
            INSERT INTO workouts (workout_date, is_rest_day)
            VALUES (%s, TRUE)
            ON CONFLICT (workout_date) DO NOTHING;
            """,
                (workout_date,),
            )
        con.commit()


def save_workout(workout: dict) -> Workout:
    workout_date_str = workout["workout_perform_date"][:10]
    workout_date = datetime.strptime(workout_date_str, "%Y-%m-%d").date()

    exercises = workout.get("exercises", [])
    exercise_count = len(exercises)
    set_count = sum(len(ex.get("sets", [])) for ex in exercises)

    description = build_workout_description(workout)

    with _get_connection() as con:
        with con.cursor() as cur:
            cur.execute(
                """
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
            ON CONFLICT (workout_date) DO NOTHING
            RETURNING workout_id, created_at;
            """,
                (
                    workout_date_str,
                    workout.get("id"),
                    workout.get("title"),
                    workout.get("total_volume"),
                    exercise_count,
                    set_count,
                    Json(description),
                ),
            )
            row = cur.fetchone()
        con.commit()

    return Workout(
        workout_date=workout_date,
        title=workout.get("title", ""),
        total_volume=workout.get("total_volume", 0),
        exercise_count=exercise_count,
        set_count=set_count,
        description=description,
        workout_id=row[0] if row else None,
        created_at=row[1] if row and len(row) > 1 else datetime.now(),
    )


def enforce_data_retention(months: int = 12):
    with _get_connection() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                DELETE FROM workouts
                WHERE workout_date < CURRENT_DATE - (%s || ' months')::interval;
            """,
                (str(months),),
            )
        con.commit()


def fetch_recent_workouts(days: int = 28) -> list[Workout]:
    with _get_connection() as con:
        with con.cursor() as cur:
            cur.execute(
                """
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
                    AND workout_date >= CURRENT_DATE - (%s || ' days')::interval
                ORDER BY workout_date ASC;
            """,
                (str(days),),
            )
            rows = cur.fetchall()

    return [
        Workout(
            workout_date=r[0],
            title=r[1],
            total_volume=r[2],
            exercise_count=r[3],
            set_count=r[4],
            description=r[5],
            is_rest_day=False,
        )
        for r in rows
    ]


def fetch_workout_summary(days: int = 21) -> WorkoutSummary:
    with _get_connection() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_days,
                    SUM(CASE WHEN is_rest_day = FALSE THEN 1 ELSE 0 END) AS workout_days,
                    SUM(CASE WHEN is_rest_day = TRUE THEN 1 ELSE 0 END) AS rest_days,
                    COALESCE(SUM(total_volume), 0) AS total_volume,
                    COALESCE(AVG(total_volume), 0) AS avg_volume,
                    COALESCE(AVG(exercise_count), 0) AS avg_exercises,
                    COALESCE(AVG(set_count), 0) AS avg_sets
                FROM workouts
                WHERE workout_date >= CURRENT_DATE - (%s || ' days')::interval;
            """,
                (str(days),),
            )
            row = cur.fetchone()

    return WorkoutSummary(
        total_days=row[0] or 0,
        workout_days=row[1] or 0,
        rest_days=row[2] or 0,
        total_volume=row[3] or 0,
        avg_volume=round(row[4] or 0, 2),
        avg_exercises=round(row[5] or 0, 2),
        avg_sets=round(row[6] or 0, 2),
    )

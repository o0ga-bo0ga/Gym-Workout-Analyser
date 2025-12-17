import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/workouts.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            workout_date TEXT PRIMARY KEY,
            workout_id INTEGER,
            title TEXT,
            total_volume INTEGER,
            exercise_count INTEGER,
            set_count INTEGER,
            raw_json TEXT,
            is_rest_day INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

def log_rest_day(workout_date):
    with get_connection() as con:
        con.execute("""
        INSERT OR IGNORE INTO workouts
        (workout_date, is_rest_day)
        VALUES (?, 1)
        """, (workout_date,))

def log_workout(workout):
    workout_date = workout["workout_perform_date"][:10]

    exercises = workout.get("exercises", [])
    exercise_count = len(exercises)
    set_count = sum(len(ex.get("sets", [])) for ex in exercises)

    with get_connection() as con:
        con.execute("""
        INSERT OR IGNORE INTO workouts
        (
            workout_date,
            workout_id,
            title,
            total_volume,
            exercise_count,
            set_count,
            raw_json,
            is_rest_day
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            workout_date,
            workout.get("id"),
            workout.get("title"),
            workout.get("total_volume"),
            exercise_count,
            set_count,
            json.dumps(workout)
        ))

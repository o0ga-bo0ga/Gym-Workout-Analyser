import sqlite3
from pathlib import Path

DB_PATH = Path("data/workouts.db")

def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            date TEXT,
            day TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

def workout_exists(workout_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM workouts WHERE id = ?", (workout_id,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def insert_workout(workout_id, date, day, content):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO workouts (id, date, day, content) VALUES (?, ?, ?, ?)",
        (workout_id, date, day, content),
    )
    conn.commit()
    conn.close()

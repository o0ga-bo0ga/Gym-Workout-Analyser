import sqlite3

DB_PATH = "data/workouts.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY,
        date TEXT,
        content TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_workout(workout_id, date, content):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO workouts (id, date, content)
    VALUES (?, ?, ?)
    """, (workout_id, date, content))

    conn.commit()
    conn.close()


def load_recent_workouts(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT content FROM workouts
    ORDER BY date DESC
    LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()

    return "\n\n".join(r[0] for r in rows)

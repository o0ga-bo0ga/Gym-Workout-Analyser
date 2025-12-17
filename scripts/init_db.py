import sqlite3

conn = sqlite3.connect("workouts.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS workouts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL,
  day TEXT NOT NULL,
  content TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database initialized successfully")

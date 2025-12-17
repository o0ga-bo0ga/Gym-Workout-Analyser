from datetime import date
from db import init_db, log_rest_day, log_workout

def persist_today(workout):
    init_db()
    today = date.today().isoformat()

    if workout is None:
        log_rest_day(today)
        print(f"PHASE2: Rest day logged for {today}")
        return

    log_workout(workout)
    print(f"PHASE2: Workout logged for {today}")

from datetime import date
from db import init_db, log_rest_day, log_workout, enforce_retention
from log import info

def persist_today(workout):
    init_db()
    today = date.today().isoformat()

    if workout is None:
        log_rest_day(today)
        info(f"PHASE2: Rest day logged for {today}")
    else:
        log_workout(workout)
        info(f"PHASE2: Workout logged for {today}")

    # Retention should never block ingestion
    try:
        enforce_retention(months=12)
        info("PHASE2: Retention enforced (12 months)")
    except Exception as e:
        info(f"PHASE2 WARNING: Retention failed: {e}")
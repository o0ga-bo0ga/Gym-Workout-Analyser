from log import info, warn, error
from db import fetch_recent_workouts
from gemini import analyze_workout
from config import LYFTA_ENABLED, DB_ENABLED, ANALYSIS_ENABLED
from phase1 import fetch_today
from phase2 import persist_today
from phase3 import summarize_last_21_days

def main():
    info("=== Daily Workout Pipeline Start ===")

    workout = None

    if LYFTA_ENABLED:
        workout = fetch_today()
    else:
        warn("LYFTA disabled, skipping fetch")

    if DB_ENABLED:
        try:
            persist_today(workout)
        except Exception as e:
            error(f"DB failure: {e}")
            raise
    else:
        warn("DB disabled, skipping persistence")

    if ANALYSIS_ENABLED and workout is not None:
        try:
            history = fetch_recent_workouts(days=28)
            info(f"GEMINI TEST: history workouts = {len(history)}")
            analysis = analyze_workout(workout, history)
            info("GEMINI ANALYSIS")
            print(analysis)
        except Exception as e:
            warn(f"Gemini analysis failed: {e}")

    info("=== Pipeline Complete ===")

if __name__ == "__main__":
    main()

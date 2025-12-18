from phase1 import fetch_today
from phase2 import persist_today
from phase3 import summarize_last_21_days
from log import info

def main():
    info("=== Daily Workout Pipeline Start ===")

    workout = fetch_today()
    persist_today(workout)
    summarize_last_21_days()

    info("=== Pipeline Complete ===")

if __name__ == "__main__":
    main()

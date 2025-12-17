from phase1 import fetch_today
from phase2 import persist_today
from phase3 import summarize_last_21_days

def main():
    print("=== Daily Workout Pipeline Start ===")

    workout = fetch_today()
    persist_today(workout)
    summarize_last_21_days()

    print("=== Pipeline Complete ===")

if __name__ == "__main__":
    main()

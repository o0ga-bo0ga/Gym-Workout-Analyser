import os
from datetime import datetime

from lyfta import fetch_workouts_since
from db import init_db, log_workout
from log import info, warn


def main():
    api_key = os.environ.get("LYFTA_API_KEY")
    if not api_key:
        raise RuntimeError("LYFTA_API_KEY not set")

    days = int(os.environ.get("BACKFILL_DAYS", "365"))

    info(f"Starting backfill for last {days} days")

    init_db()

    workouts = fetch_workouts_since(api_key, days=days)
    info(f"Fetched {len(workouts)} workouts from Lyfta")

    inserted = 0
    skipped = 0

    for w in workouts:
        try:
            log_workout(w)
            inserted += 1
        except Exception as e:
            # Most common case: duplicate (already exists)
            skipped += 1
            warn(f"Skipping workout on {w.get('workout_perform_date')}: {e}")

    info(f"Backfill complete — inserted={inserted}, skipped={skipped}")


if __name__ == "__main__":
    main()

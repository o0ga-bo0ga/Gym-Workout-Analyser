import json
import os

from config import (
    ANALYSIS_ENABLED,
    BACKFILL_DATE,
    DATABASE_ENABLED,
    DRY_RUN,
    LLM_PROVIDER,
    LYFTA_ENABLED,
    SKIP_DB_SAVE,
    TONE,
)
from data_fetch import fetch_today_workout, fetch_workout_for_target_date
from database import fetch_recent_workouts, workout_exists_for_date
from discord_client import (
    format_discord_embed,
    send_discord_embed,
    send_discord_message,
)
from llm_client import analyze_workout
from log import error, info, warn
from persistence import persist_today_workout, persist_workout_for_date

REST_DAY_MESSAGE: str = os.environ.get(
    "REST_DAY_MESSAGE", "Rest day taken. Recovery is important!"
)


def main() -> None:
    info("=== Daily Workout Pipeline Start ===")

    workout: dict | None = None
    target_date: str | None = None

    if BACKFILL_DATE:
        target_date = BACKFILL_DATE
        info(f"BACKFILL mode: target_date = {target_date}")
        if LYFTA_ENABLED:
            workout = fetch_workout_for_target_date(target_date)
        else:
            warn("LYFTA disabled, skipping backfill fetch")
    elif LYFTA_ENABLED:
        workout = fetch_today_workout()
    else:
        warn("LYFTA disabled, skipping fetch")

    if target_date is not None and workout is not None:
        if DATABASE_ENABLED and not SKIP_DB_SAVE:
            try:
                if workout_exists_for_date(target_date):
                    info(
                        f"DB: Workout for {target_date} already exists, skipping persist"
                    )
                else:
                    persist_workout_for_date(workout, target_date)
            except Exception as e:
                error(f"Database failure: {e}")
                raise
        elif SKIP_DB_SAVE:
            info("SKIP_DB_SAVE set, skipping DB persistence")
        else:
            warn("Database disabled, skipping persistence")
    elif DATABASE_ENABLED:
        try:
            persist_today_workout(workout)
        except Exception as e:
            error(f"Database failure: {e}")
            raise
    else:
        warn("Database disabled, skipping persistence")

    if workout is None:
        try:
            send_discord_message(REST_DAY_MESSAGE)
            info("Rest day reported")
        except Exception as e:
            warn(f"Rest day Discord send failed: {e}")
    elif ANALYSIS_ENABLED:
        try:
            history_28_days = fetch_recent_workouts(days=28)
            info(f"{LLM_PROVIDER.upper()}: history workouts = {len(history_28_days)}")

            history_dicts = [w.to_dict() for w in history_28_days]
            workout_dict = (
                workout if isinstance(workout, dict) else workout.to_dict()
            )

            analysis = analyze_workout(workout_dict, history_dicts, tone=TONE)
            info(f"TONE: {TONE}")

            embed = format_discord_embed(analysis, workout_dict)
            send_discord_embed(embed)
            info("Discord report sent")
            print(json.dumps(analysis, indent=2))
        except Exception as e:
            warn(f"Analysis or Discord send failed: {e}")
            if not DRY_RUN:
                raise

    info("=== Pipeline Complete ===")


if __name__ == "__main__":
    main()

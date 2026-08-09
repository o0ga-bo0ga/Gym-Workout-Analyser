import json
import os

from config import (
    ANALYSIS_ENABLED,
    DATABASE_ENABLED,
    DRY_RUN,
    LLM_PROVIDER,
    LYFTA_ENABLED,
    MATCH_POOL_DAYS,
    TONE,
)
from data_fetch import fetch_today_workout
from database import fetch_recent_workouts
from discord_client import (
    format_discord_embed,
    send_discord_embed,
    send_discord_message,
)
from llm_client import analyze_workout
from log import error, info, warn
from persistence import persist_today_workout

REST_DAY_MESSAGE: str = os.environ.get(
    "REST_DAY_MESSAGE", "Rest day taken. Recovery is important!"
)


def main() -> None:
    info("=== Daily Workout Pipeline Start ===")

    workout: dict | None = None

    if LYFTA_ENABLED:
        workout = fetch_today_workout()
    else:
        warn("LYFTA disabled, skipping fetch")

    if DATABASE_ENABLED:
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
            history_pool = fetch_recent_workouts(days=MATCH_POOL_DAYS)
            info(f"{LLM_PROVIDER.upper()}: history workouts = {len(history_pool)}")

            history_dicts = [w.to_dict() for w in history_pool]
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

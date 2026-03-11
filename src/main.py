import os
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable

from config import ANALYSIS_ENABLED, DB_ENABLED, DRY_RUN, LYFTA_ENABLED
from log import error, info, warn

Workout = dict[str, Any]
History = list[dict[str, Any]]

REST_DAY_MESSAGE = "Rest day logged. Recover well and hit the next session hard."
HISTORY_WINDOW_DAYS = 28


@dataclass(frozen=True)
class PipelineSettings:
    lyfta_enabled: bool = LYFTA_ENABLED
    db_enabled: bool = DB_ENABLED
    analysis_enabled: bool = ANALYSIS_ENABLED
    history_window_days: int = HISTORY_WINDOW_DAYS
    rest_day_message: str = REST_DAY_MESSAGE


@dataclass(frozen=True)
class PipelineServices:
    fetch_today: Callable[[], Workout | None]
    persist_today: Callable[[Workout | None], None]
    fetch_recent_workouts: Callable[[int], History]
    analyze_workout: Callable[[Workout, History], str]
    format_discord_message: Callable[[str, Workout], str]
    send_discord_message: Callable[[str], None]


def fetch_today() -> Workout | None:
    """Fetch today's workout from Lyfta API."""
    from lyfta import get_todays_workout

    api_key = os.environ.get("LYFTA_API_KEY")
    if not api_key:
        raise RuntimeError("LYFTA_API_KEY not set")

    workout = get_todays_workout(api_key)
    if workout is None:
        info("PHASE1: Rest day detected")
        return None

    info("PHASE1: Workout detected")
    info(f"  Title: {workout.get('title')}")
    info(f"  Date: {workout.get('workout_perform_date')}")
    info(f"  Exercises: {len(workout.get('exercises', []))}")
    return workout


def persist_today(workout: Workout | None) -> None:
    """Persist workout or rest day to the database."""
    from db import enforce_retention, init_db, log_rest_day, log_workout

    if DRY_RUN:
        info("DRY RUN: Skipping DB write")
        return

    init_db()
    today = date.today().isoformat()

    if workout is None:
        log_rest_day(today)
        info(f"PHASE2: Rest day logged for {today}")
    else:
        log_workout(workout)
        info(f"PHASE2: Workout logged for {today}")

    # Retention should never block ingestion.
    try:
        enforce_retention(months=12)
        info("PHASE2: Retention enforced (12 months)")
    except Exception as exc:
        info(f"PHASE2 WARNING: Retention failed: {exc}")


def build_default_services() -> PipelineServices:
    from db import fetch_recent_workouts
    from discord import format_discord_message, send_discord_message
    from gemini import analyze_workout

    return PipelineServices(
        fetch_today=fetch_today,
        persist_today=persist_today,
        fetch_recent_workouts=fetch_recent_workouts,
        analyze_workout=analyze_workout,
        format_discord_message=format_discord_message,
        send_discord_message=send_discord_message,
    )


def run_pipeline(services: PipelineServices, settings: PipelineSettings) -> None:
    info("=== Daily Workout Pipeline Start ===")

    workout: Workout | None = None

    if settings.lyfta_enabled:
        workout = services.fetch_today()
    else:
        warn("LYFTA disabled, skipping fetch")

    if settings.db_enabled:
        try:
            services.persist_today(workout)
        except Exception as exc:
            error(f"DB failure: {exc}")
            raise
    else:
        warn("DB disabled, skipping persistence")

    if settings.analysis_enabled and workout is not None:
        try:
            history = services.fetch_recent_workouts(settings.history_window_days)
            info(f"GEMINI TEST: history workouts = {len(history)}")
            analysis = services.analyze_workout(workout, history)
            message = services.format_discord_message(analysis, workout)
            services.send_discord_message(message)
            info("Discord report sent")
            print(analysis)
        except Exception as exc:
            warn(f"Gemini analysis or Discord send failed: {exc}")
    else:
        try:
            services.send_discord_message(settings.rest_day_message)
            info("Rest Day reported")
        except Exception as exc:
            warn(f"Rest day Discord send failed: {exc}")

    info("=== Pipeline Complete ===")


def main() -> None:
    run_pipeline(build_default_services(), PipelineSettings())


if __name__ == "__main__":
    main()

import os

import requests

from utils.retry import retry


def send_discord_message(text):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL not set")

    payload = {
        "content": text
    }

    resp = requests.post(webhook_url, json=payload, timeout=10)

    if resp.status_code >= 500:
        raise RuntimeError(f"Discord server error: {resp.status_code}")

    resp.raise_for_status()


@retry(max_attempts=3, backoff_factor=2, initial_delay=1, exceptions=(requests.RequestException, RuntimeError))
def send_discord_message_with_retry(text):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL not set")

    payload = {
        "content": text
    }

    resp = requests.post(webhook_url, json=payload, timeout=10)

    if resp.status_code >= 500:
        raise RuntimeError(f"Discord server error: {resp.status_code}")

    resp.raise_for_status()


def format_discord_message(analysis, workout):
    title = workout.get("title", "Workout")
    date = workout.get("workout_perform_date", "").split(" ")[0]

    return f"""**🏋️ Workout Report**
**{title}** — {date}

{analysis}
"""

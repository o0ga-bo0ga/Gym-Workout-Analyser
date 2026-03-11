import os
from typing import Any

import requests

from config import DISCORD_TIMEOUT_SECONDS


def send_discord_message(text: str) -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL not set")

    payload = {
        "content": text
    }

    resp = requests.post(
        webhook_url,
        json=payload,
        timeout=DISCORD_TIMEOUT_SECONDS,
    )
    if resp.status_code >= 400:
        raise RuntimeError(f"Discord webhook failed {resp.status_code}: {resp.text}")


def format_discord_message(analysis: str, workout: dict[str, Any]) -> str:
    title = workout.get("title", "Workout")
    date = workout.get("workout_perform_date", "").split(" ")[0]

    return f"""**🏋️ Workout Report**
**{title}** — {date}

{analysis}
"""

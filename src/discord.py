import os
from typing import Any

import requests

from config import DISCORD_TIMEOUT_SECONDS

MAX_DISCORD_CONTENT_LENGTH = 2000


def _chunk_content(text: str, max_length: int = MAX_DISCORD_CONTENT_LENGTH) -> list[str]:
    if not text:
        return [""]
    chunks: list[str] = []
    remaining = text

    while remaining:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break

        split_at = max(
            remaining.rfind("\n", 0, max_length + 1),
            remaining.rfind(" ", 0, max_length + 1),
        )

        # No safe boundary found (e.g. one very long token); hard-split.
        if split_at <= 0:
            split_at = max_length
            next_start = split_at
        else:
            next_start = split_at + 1

        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[next_start:].lstrip()

    return chunks


def send_discord_message(text: str) -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL not set")

    for chunk in _chunk_content(text):
        payload = {"content": chunk}
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

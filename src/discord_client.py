import json
import os

import requests

from utils.retry import retry


def send_discord_message(text):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL not set")

    payload = {"content": text}
    resp = requests.post(webhook_url, json=payload, timeout=10)

    if resp.status_code >= 500:
        raise RuntimeError(f"Discord server error: {resp.status_code}")
    resp.raise_for_status()


def send_discord_embed(embed: dict):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL not set")

    payload = {"embeds": [embed]}
    resp = requests.post(webhook_url, json=payload, timeout=10)

    if resp.status_code >= 500:
        raise RuntimeError(f"Discord server error: {resp.status_code}")
    resp.raise_for_status()


@retry(
    max_attempts=3,
    backoff_factor=2,
    initial_delay=1,
    exceptions=(requests.RequestException, RuntimeError),
)
def send_discord_message_with_retry(text):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL not set")

    payload = {"content": text}
    resp = requests.post(webhook_url, json=payload, timeout=10)

    if resp.status_code >= 500:
        raise RuntimeError(f"Discord server error: {resp.status_code}")
    resp.raise_for_status()


def _truncate(text: str, max_len: int = 1024) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def format_discord_embed(analysis: dict, workout: dict) -> dict:
    title = workout.get("title", "Workout")
    date = workout.get("workout_perform_date", "").split(" ")[0]
    volume = workout.get("total_volume", "N/A")

    if "raw_text" in analysis:
        return {
            "title": f"Workout Report — {title}",
            "description": _truncate(analysis["raw_text"], 4000),
            "color": 0x5865F2,
            "fields": [],
            "footer": {"text": date},
        }

    fields = []

    progression = analysis.get("progression", "N/A")
    fields.append(
        {"name": "Progression", "value": _truncate(progression), "inline": False}
    )

    coverage = analysis.get("coverage", "")
    if coverage:
        fields.append(
            {"name": "Exercise Coverage", "value": _truncate(coverage), "inline": False}
        )

    fatigue = analysis.get("fatigue", "None detected.")
    fields.append(
        {"name": "Fatigue Signals", "value": _truncate(fatigue), "inline": False}
    )

    vol_dist = analysis.get("volume_distribution", "")
    if vol_dist:
        fields.append(
            {
                "name": "Volume Distribution",
                "value": _truncate(vol_dist),
                "inline": False,
            }
        )

    positives = analysis.get("positives", [])
    if positives:
        text = "\n".join(f"+ {p}" for p in positives)
        fields.append(
            {"name": "What Went Well", "value": _truncate(text), "inline": False}
        )

    improvements = analysis.get("improvements", [])
    if improvements:
        text = "\n".join(f"- {i}" for i in improvements)
        fields.append({"name": "To Improve", "value": _truncate(text), "inline": False})
    else:
        fields.append(
            {"name": "To Improve", "value": "Nothing flagged.", "inline": False}
        )

    next_session = analysis.get("next_session", "N/A")
    fields.append(
        {"name": "Next Session", "value": _truncate(next_session), "inline": False}
    )

    color = 0x57F287
    if improvements:
        color = 0xFEE75C
    if fatigue and fatigue != "None detected.":
        color = 0xED4245

    return {
        "title": f"Workout Report — {title}",
        "description": f"**{volume}** kg total volume",
        "color": color,
        "fields": fields,
        "footer": {"text": date},
    }


def format_discord_message(analysis, workout):
    title = workout.get("title", "Workout")
    date = workout.get("workout_perform_date", "").split(" ")[0]

    if isinstance(analysis, dict) and "raw_text" not in analysis:
        embed = format_discord_embed(analysis, workout)
        return embed

    if isinstance(analysis, dict):
        text = analysis.get("raw_text", json.dumps(analysis, indent=2))
    else:
        text = str(analysis)

    return f"""**Workout Report**
**{title}** — {date}

{text}
"""

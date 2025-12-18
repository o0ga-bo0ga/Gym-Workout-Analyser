import os
import requests

def send_discord_message(text):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("DISCORD_WEBHOOK_URL not set")

    payload = {
        "content": text
    }

    resp = requests.post(webhook_url, json=payload, timeout=10)
    resp.raise_for_status()

def format_discord_message(analysis, workout):
    title = workout.get("title", "Workout")
    date = workout.get("workout_perform_date", "").split(" ")[0]

    return f"""**🏋️ Workout Report**
**{title}** — {date}

{analysis}
"""

from datetime import date

import requests

from utils.retry import retry

BASE_URL = "https://my.lyfta.app"


@retry(
    max_attempts=3,
    backoff_factor=2,
    initial_delay=2,
    exceptions=(requests.RequestException,),
)
def fetch_todays_workout(api_key):
    headers = {"Authorization": f"Bearer {api_key}"}

    params = {"limit": 1, "page": 1}

    resp = requests.get(
        f"{BASE_URL}/api/v1/workouts", headers=headers, params=params, timeout=10
    )

    if resp.status_code != 200:
        raise RuntimeError(f"Lyfta API failed {resp.status_code}: {resp.text}")

    data = resp.json()
    workouts = data.get("workouts", [])

    if not workouts:
        return None

    latest = workouts[0]
    workout_date = latest.get("workout_perform_date", "")[:10]

    if workout_date == date.today().isoformat():
        return latest

    return None


@retry(
    max_attempts=3,
    backoff_factor=2,
    initial_delay=2,
    exceptions=(requests.RequestException,),
)
def fetch_workout_for_date(api_key: str, target_date: str) -> dict | None:
    headers = {"Authorization": f"Bearer {api_key}"}

    params = {"limit": 50, "page": 1}

    resp = requests.get(
        f"{BASE_URL}/api/v1/workouts", headers=headers, params=params, timeout=10
    )

    if resp.status_code != 200:
        raise RuntimeError(f"Lyfta API failed {resp.status_code}: {resp.text}")

    workouts = resp.json().get("workouts", [])

    for w in workouts:
        if w.get("workout_perform_date", "")[:10] == target_date:
            return w

    return None

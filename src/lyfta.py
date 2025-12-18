import requests
from datetime import date, datetime, timedelta
from time import sleep

BASE_URL = "https://my.lyfta.app"

def get_todays_workout(api_key):
    for attempt in (1,2):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}"
            }

            params = {
                "limit": 1,
                "page": 1
            }

            resp = requests.get(
                f"{BASE_URL}/api/v1/workouts",
                headers=headers,
                params=params,
                timeout=10
            )

            if resp.status_code != 200:
                raise RuntimeError(
                    f"Lyfta API failed {resp.status_code}: {resp.text}"
                )

            data = resp.json()
            workouts = data.get("workouts", [])

            if not workouts:
                return None

            latest = workouts[0]
            workout_date = latest.get("workout_perform_date", "")[:10]

            if workout_date == date.today().isoformat():
                return latest

            return None
        except requests.RequestException as e:
            if attempt == 2:
                raise
            sleep(2)
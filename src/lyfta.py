import requests
from datetime import date, timedelta
from time import sleep

BASE_URL = "https://my.lyfta.app"

def fetch_workouts_since(api_key, days=365):
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    cutoff_date = datetime.utcnow() - timedelta(days=days)
    page = 1
    all_workouts = []

    while True:
        params = {
            "limit": 100,
            "page": page,
        }

        resp = requests.get(
            f"{BASE_URL}/api/v1/workouts",
            headers=headers,
            params=params,
            timeout=15
        )
        resp.raise_for_status()

        data = resp.json()
        workouts = data.get("workouts", [])

        if not workouts:
            break

        for w in workouts:
            date_str = w.get("workout_perform_date")
            if not date_str:
                continue

            workout_date = datetime.fromisoformat(date_str[:19])
            if workout_date < cutoff_date:
                return all_workouts  # stop early

            all_workouts.append(w)

        if page >= data.get("total_pages", 1):
            break

        page += 1

    return all_workouts




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
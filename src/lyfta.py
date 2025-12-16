import requests

BASE_URL = "https://my.lyfta.app/api/v1/workouts"

def fetch_latest_workout(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    params = {
        "limit": 1,
        "page": 1
    }

    resp = requests.get(BASE_URL, headers=headers, params=params)
    resp.raise_for_status()

    data = resp.json()

    workouts = data.get("workouts", [])
    if not workouts:
        return None

    return workouts[0]

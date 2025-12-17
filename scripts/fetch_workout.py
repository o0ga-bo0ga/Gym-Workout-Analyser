import os
import requests

API_KEY = os.environ["LYFTA_API_KEY"]
BASE_URL = "https://my.lyfta.app/api/v1/workouts"

def fetch_latest_workout():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    params = {
        "limit": 1,
        "page": 1
    }

    resp = requests.get(BASE_URL, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()

    workouts = data["workouts"]
    if not workouts:
        return None

    return workouts[0]

import os
import json
from datetime import date
from dateutil import parser
import requests

# Config
API_KEY = os.getenv('LYFTA_API_KEY')
if not API_KEY:
    raise ValueError("Set LYFTA_API_KEY env var with your API key.")

BASE_URL = 'https://my.lyfta.app'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}
TODAY = date(2025, 12, 17)  # Hardcoded for testing; use date.today() in prod
TODAY_STR = TODAY.isoformat()  # '2025-12-17'

def fetch_recent_workouts():
    """Fetch recent workouts (limit=10, page=1)."""
    params = {'limit': 10, 'page': 1}
    response = requests.get(f'{BASE_URL}/api/v1/workouts', headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('status'):
            return data.get('workouts', [])
    print(f"Error {response.status_code}: {response.text}")
    return []

def build_description(exercises):
    """Format exercises/sets as text."""
    if not exercises:
        return "No exercises logged."
    desc_parts = []
    for ex in exercises:
        name = ex.get('excercise_name', 'Unknown')
        sets = ex.get('sets', [])
        sets_str = []
        for s in sets:
            weight = s.get('weight', '0')
            reps = s.get('reps', '0')
            completed = 'completed' if s.get('is_completed') else 'incomplete'
            sets_str.append(f"{weight}kg x {reps} reps ({completed})")
        desc_parts.append(f"{name}: {', '.join(sets_str)}")
    return '; '.join(desc_parts)

def get_todays_workout():
    """Find today's workout or return rest."""
    workouts = fetch_recent_workouts()
    today_workout = None
    for w in workouts:
        perform_date_str = w.get('workout_perform_date', '')
        try:
            perform_date = parser.parse(perform_date_str).date()
            if perform_date == TODAY:
                today_workout = w
                break
        except ValueError:
            continue  # Skip invalid dates
    
    if today_workout:
        title = today_workout.get('title', 'Untitled Workout')
        description = build_description(today_workout.get('exercises', []))
        day_name = TODAY.strftime('%A')  # e.g., 'Tuesday'
        return {
            'date': TODAY_STR,
            'day': day_name,
            'title': title,
            'description': description,
            'type': 'workout'
        }
    else:
        return {
            'date': TODAY_STR,
            'day': TODAY.strftime('%A'),
            'title': 'Rest Day',
            'description': 'No workout logged.',
            'type': 'rest'
        }

if __name__ == '__main__':
    result = get_todays_workout()
    print(json.dumps(result, indent=2))
    print(f"\nType: {result['type']}")

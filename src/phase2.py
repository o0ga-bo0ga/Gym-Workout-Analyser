from datetime import date
from db import init_db, log_rest_day, log_workout

def persist_today(workout):
    init_db()
    today = date.today().isoformat()

    if workout is None:
        log_rest_day(today)
        print(f"PHASE2: Rest day logged for {today}")
        return

    log_workout(workout)
    print(f"PHASE2: Workout logged for {today}")
    
def build_workout_description(workout):
    """
    Returns a dict:
    {
      exercise_name: [
        { weight_kg: int/float, reps: int },
        ...
      ],
      ...
    }
    """
    description = {}

    for ex in workout.get("exercises", []):
        name = ex.get("excercise_name")
        sets_data = []

        for s in ex.get("sets", []):
            weight = s.get("weight")
            reps = s.get("reps")

            if weight is None or reps is None:
                continue

            sets_data.append({
                "weight_kg": float(weight),
                "reps": int(reps)
            })

        if sets_data:
            description[name] = sets_data

    return description

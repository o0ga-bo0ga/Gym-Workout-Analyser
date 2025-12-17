import os
from lyfta import get_todays_workout

def main():
    api_key = os.environ.get("LYFTA_API_KEY")
    if not api_key:
        raise RuntimeError("LYFTA_API_KEY not set")

    workout = get_todays_workout(api_key)

    if workout is None:
        print("PHASE1 RESULT: Rest day (no workout logged today)")
        return

    print("PHASE1 RESULT: Workout detected today")
    print(f"Title: {workout.get('title')}")
    print(f"Date: {workout.get('workout_perform_date')}")
    print(f"Total volume: {workout.get('total_volume')}")
    print("")

    exercises = workout.get("exercises", [])
    print(f"Exercises count: {len(exercises)}")
    print("-" * 40)

    for ex in exercises:
        name = ex.get("excercise_name")
        ex_type = ex.get("exercise_type")

        print(f"Exercise: {name} ({ex_type})")

        sets = ex.get("sets", [])
        for idx, s in enumerate(sets, start=1):
            weight = s.get("weight")
            reps = s.get("reps")

            print(
                f"  Set {idx}: {weight} kg x {reps} "
            )

        print("")

if __name__ == "__main__":
    main()

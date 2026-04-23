from src.workout_transformer import build_workout_description


def test_build_workout_description_basic(sample_workout, sample_workout_description):
    result = build_workout_description(sample_workout)
    assert result == sample_workout_description


def test_build_workout_description_empty_exercises():
    workout = {"exercises": []}
    result = build_workout_description(workout)
    assert result == {}


def test_build_workout_description_missing_exercises():
    workout = {}
    result = build_workout_description(workout)
    assert result == {}


def test_build_workout_description_exercise_with_no_name():
    workout = {
        "exercises": [
            {"sets": [{"weight": 30, "reps": 10}]}
        ]
    }
    result = build_workout_description(workout)
    assert result == {}


def test_build_workout_description_sets_with_missing_values():
    workout = {
        "exercises": [
            {
                "excercise_name": "Test Exercise",
                "sets": [
                    {"weight": None, "reps": 10},
                    {"weight": 30, "reps": None}
                ]
            }
        ]
    }
    result = build_workout_description(workout)
    assert result == {}


def test_build_workout_description_exercise_with_all_valid_sets():
    workout = {
        "exercises": [
            {
                "excercise_name": "Test Exercise",
                "sets": [
                    {"weight": 30, "reps": 10},
                    {"weight": 30, "reps": 8},
                    {"weight": 30, "reps": 6}
                ]
            }
        ]
    }
    result = build_workout_description(workout)
    assert "Test Exercise" in result
    assert len(result["Test Exercise"]) == 3
    assert result["Test Exercise"][0] == {"weight_kg": 30.0, "reps": 10}


def test_build_workout_description_weights_are_floats():
    workout = {
        "exercises": [
            {
                "excercise_name": "Test",
                "sets": [
                    {"weight": 30, "reps": 10}
                ]
            }
        ]
    }
    result = build_workout_description(workout)
    assert isinstance(result["Test"][0]["weight_kg"], float)


def test_build_workout_description_reps_are_ints():
    workout = {
        "exercises": [
            {
                "excercise_name": "Test",
                "sets": [
                    {"weight": 30, "reps": 10}
                ]
            }
        ]
    }
    result = build_workout_description(workout)
    assert isinstance(result["Test"][0]["reps"], int)

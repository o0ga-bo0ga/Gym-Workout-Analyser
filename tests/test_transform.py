"""Tests for transform.py - workout data transformation."""

from transform import build_workout_description


class TestBuildWorkoutDescription:
    """Tests for build_workout_description function."""

    def test_empty_workout_returns_empty_dict(self):
        """Empty workout should return empty description."""
        workout = {"exercises": []}
        result = build_workout_description(workout)
        assert result == {}

    def test_workout_without_exercises_key_returns_empty(self):
        """Workout without exercises key should return empty description."""
        workout = {}
        result = build_workout_description(workout)
        assert result == {}

    def test_single_exercise_single_set(self):
        """Single exercise with one set should be properly transformed."""
        workout = {
            "exercises": [
                {
                    "excercise_name": "Bench Press",
                    "sets": [{"weight": 100, "reps": 10}]
                }
            ]
        }
        result = build_workout_description(workout)
        
        assert "Bench Press" in result
        assert len(result["Bench Press"]) == 1
        assert result["Bench Press"][0] == {"weight_kg": 100.0, "reps": 10}

    def test_single_exercise_multiple_sets(self):
        """Single exercise with multiple sets."""
        workout = {
            "exercises": [
                {
                    "excercise_name": "Squat",
                    "sets": [
                        {"weight": 80, "reps": 12},
                        {"weight": 90, "reps": 10},
                        {"weight": 100, "reps": 8}
                    ]
                }
            ]
        }
        result = build_workout_description(workout)
        
        assert "Squat" in result
        assert len(result["Squat"]) == 3
        assert result["Squat"][0]["weight_kg"] == 80.0
        assert result["Squat"][2]["reps"] == 8

    def test_multiple_exercises(self):
        """Multiple exercises should all be included."""
        workout = {
            "exercises": [
                {
                    "excercise_name": "Bench Press",
                    "sets": [{"weight": 100, "reps": 10}]
                },
                {
                    "excercise_name": "Shoulder Press",
                    "sets": [{"weight": 40, "reps": 12}]
                }
            ]
        }
        result = build_workout_description(workout)
        
        assert len(result) == 2
        assert "Bench Press" in result
        assert "Shoulder Press" in result

    def test_skips_exercise_without_name(self):
        """Exercises without name should be skipped."""
        workout = {
            "exercises": [
                {
                    "sets": [{"weight": 100, "reps": 10}]
                },
                {
                    "excercise_name": "Valid Exercise",
                    "sets": [{"weight": 50, "reps": 15}]
                }
            ]
        }
        result = build_workout_description(workout)
        
        assert len(result) == 1
        assert "Valid Exercise" in result

    def test_skips_sets_with_missing_weight(self):
        """Sets without weight should be skipped."""
        workout = {
            "exercises": [
                {
                    "excercise_name": "Curl",
                    "sets": [
                        {"weight": 20, "reps": 12},
                        {"reps": 10},  # Missing weight
                        {"weight": 25, "reps": 10}
                    ]
                }
            ]
        }
        result = build_workout_description(workout)
        
        assert len(result["Curl"]) == 2

    def test_skips_sets_with_missing_reps(self):
        """Sets without reps should be skipped."""
        workout = {
            "exercises": [
                {
                    "excercise_name": "Curl",
                    "sets": [
                        {"weight": 20, "reps": 12},
                        {"weight": 22},  # Missing reps
                    ]
                }
            ]
        }
        result = build_workout_description(workout)
        
        assert len(result["Curl"]) == 1

    def test_exercise_with_all_invalid_sets_is_excluded(self):
        """Exercise with only invalid sets should not appear in result."""
        workout = {
            "exercises": [
                {
                    "excercise_name": "Bad Exercise",
                    "sets": [
                        {"weight": None, "reps": 10},
                        {"weight": 50, "reps": None}
                    ]
                }
            ]
        }
        result = build_workout_description(workout)
        
        assert "Bad Exercise" not in result
        assert result == {}

    def test_weight_converted_to_float(self):
        """Weight should be converted to float."""
        workout = {
            "exercises": [
                {
                    "excercise_name": "Press",
                    "sets": [{"weight": "55.5", "reps": 10}]
                }
            ]
        }
        result = build_workout_description(workout)
        
        assert result["Press"][0]["weight_kg"] == 55.5
        assert isinstance(result["Press"][0]["weight_kg"], float)

    def test_reps_converted_to_int(self):
        """Reps should be converted to int."""
        workout = {
            "exercises": [
                {
                    "excercise_name": "Press",
                    "sets": [{"weight": 50, "reps": "12"}]
                }
            ]
        }
        result = build_workout_description(workout)
        
        assert result["Press"][0]["reps"] == 12
        assert isinstance(result["Press"][0]["reps"], int)

"""Tests for shared workout parsing utilities."""

from workout_utils import get_exercise_name, parse_weight_reps


def test_get_exercise_name_with_legacy_key():
    assert get_exercise_name({"excercise_name": "Bench"}) == "Bench"


def test_get_exercise_name_with_new_key():
    assert get_exercise_name({"exercise_name": "Squat"}) == "Squat"


def test_parse_weight_reps_returns_none_for_invalid():
    assert parse_weight_reps({"weight": "bad", "reps": 10}) is None
    assert parse_weight_reps({"weight": 50, "reps": None}) is None


def test_parse_weight_reps_parses_valid_values():
    assert parse_weight_reps({"weight": "45.5", "reps": "8"}) == (45.5, 8)

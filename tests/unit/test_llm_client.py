from datetime import date, timedelta

from src.llm_client import (
    _dominant_muscle_group,
    _filter_recent_window,
    _select_similar_sessions,
    _validate_and_correct,
    build_prompt,
)


def _workout(workout_date: str, exercises: dict) -> dict:
    """Build a DB-shaped workout dict (as returned by Workout.to_dict())."""
    description = {
        name: [{"weight_kg": w, "reps": r} for w, r in sets]
        for name, sets in exercises.items()
    }
    total_volume = sum(w * r for sets in exercises.values() for w, r in sets)
    return {
        "date": workout_date,
        "workout_perform_date": f"{workout_date} 00:00:00",
        "title": "Test",
        "total_volume": total_volume,
        "description": description,
    }


def chest_day(workout_date: str) -> dict:
    return _workout(workout_date, {"Bench Press": [(60, 8), (60, 8)]})


def leg_day(workout_date: str) -> dict:
    return _workout(workout_date, {"Squat": [(80, 8), (80, 8)]})


def back_day(workout_date: str) -> dict:
    return _workout(workout_date, {"Barbell Row": [(50, 10)]})


class TestDominantMuscleGroup:
    def test_empty_workout_returns_none(self):
        assert _dominant_muscle_group({"description": {}}) is None

    def test_unmatched_exercise_returns_none(self):
        workout = _workout("2026-01-01", {"Mystery Machine": [(10, 10)]})
        assert _dominant_muscle_group(workout) is None

    def test_single_group_returns_that_group(self):
        assert _dominant_muscle_group(chest_day("2026-01-01")) == "chest"

    def test_tie_resolves_deterministically(self):
        workout = _workout(
            "2026-01-01",
            {"Bench Press": [(50, 10)], "Barbell Row": [(50, 10)]},
        )
        # Equal volume chest vs back; whichever exercise appears first wins.
        assert _dominant_muscle_group(workout) == "chest"

    def test_leg_curl_is_not_shadowed_by_generic_biceps_curl_keyword(self):
        # Regression test: "curl" (biceps) must not out-match the more
        # specific "leg curl" (legs) just because biceps is checked first.
        workout = _workout(
            "2026-01-01",
            {"Smith Full Squat": [(80, 8)], "Lever Seated Leg Curl": [(50, 10)]},
        )
        assert _dominant_muscle_group(workout) == "legs"


class TestSelectSimilarSessions:
    def test_filters_to_matching_dominant_group(self):
        today = chest_day("2026-02-01")
        history = [
            chest_day("2026-01-25"),
            leg_day("2026-01-27"),
            back_day("2026-01-29"),
        ]
        result = _select_similar_sessions(today, history, limit=3)
        assert [h["date"] for h in result] == ["2026-01-25"]

    def test_caps_at_limit_keeping_most_recent(self):
        today = chest_day("2026-02-10")
        history = [chest_day(f"2026-01-0{i}") for i in range(1, 6)]
        result = _select_similar_sessions(today, history, limit=3)
        assert [h["date"] for h in result] == ["2026-01-03", "2026-01-04", "2026-01-05"]

    def test_chronological_order_preserved(self):
        today = chest_day("2026-02-10")
        history = [chest_day("2026-01-05"), chest_day("2026-01-01"), chest_day("2026-01-03")]
        result = _select_similar_sessions(today, history, limit=3)
        assert [h["date"] for h in result] == ["2026-01-01", "2026-01-03", "2026-01-05"]

    def test_empty_history_returns_empty(self):
        assert _select_similar_sessions(chest_day("2026-01-01"), [], limit=3) == []

    def test_today_with_no_dominant_group_returns_empty(self):
        today = {"description": {}}
        history = [chest_day("2026-01-01")]
        assert _select_similar_sessions(today, history, limit=3) == []


class TestFilterRecentWindow:
    def test_includes_within_window_excludes_outside(self):
        in_window = (date.today() - timedelta(days=5)).isoformat()
        out_window = (date.today() - timedelta(days=20)).isoformat()
        history = [chest_day(in_window), leg_day(out_window)]

        result = _filter_recent_window(history, window_days=14)

        assert [h["date"] for h in result] == [in_window]

    def test_boundary_at_exactly_window_days_is_included(self):
        boundary = (date.today() - timedelta(days=14)).isoformat()
        history = [chest_day(boundary)]

        result = _filter_recent_window(history, window_days=14)

        assert [h["date"] for h in result] == [boundary]

    def test_empty_history_returns_empty(self):
        assert _filter_recent_window([], window_days=14) == []


class TestBuildPromptSections:
    def test_includes_both_history_sections(self):
        today = chest_day(date.today().isoformat())
        history = [chest_day((date.today() - timedelta(days=5)).isoformat())]

        prompt = build_prompt(today, history, tone="balanced")

        assert "SIMILAR PAST SESSIONS" in prompt
        assert "RECENT TRAINING WINDOW" in prompt

    def test_empty_history_shows_graceful_text(self):
        today = chest_day(date.today().isoformat())

        prompt = build_prompt(today, [], tone="balanced")

        assert "No prior sessions with a matching dominant muscle group yet." in prompt
        assert "No other workouts recorded in this window." in prompt

    def test_leg_day_history_excluded_from_similar_sessions_for_chest_day(self):
        today = chest_day(date.today().isoformat())
        history = [leg_day((date.today() - timedelta(days=3)).isoformat())]

        prompt = build_prompt(today, history, tone="balanced")

        # The leg day still shows up under the weekly coverage window...
        assert "Squat" in prompt
        # ...but not as a "similar" progression comparison for a chest day.
        assert "No prior sessions with a matching dominant muscle group yet." in prompt


class TestValidateAndCorrect:
    def test_raw_text_passthrough(self):
        analysis = {"raw_text": "not json"}
        result = _validate_and_correct(analysis, chest_day(date.today().isoformat()), [])
        assert result == {"raw_text": "not json"}

    def test_forces_no_baseline_yet_when_similar_is_empty(self):
        today = chest_day(date.today().isoformat())
        analysis = {"progression": "Volume increased nicely today."}
        result = _validate_and_correct(analysis, today, [])
        assert result["progression"] == "No baseline yet."

    def test_leaves_correct_no_baseline_wording_alone(self):
        today = chest_day(date.today().isoformat())
        analysis = {"progression": "No baseline yet."}
        result = _validate_and_correct(analysis, today, [])
        assert result["progression"] == "No baseline yet."

    def test_does_not_touch_progression_when_similar_sessions_exist(self):
        today = chest_day(date.today().isoformat())
        history = [chest_day((date.today() - timedelta(days=5)).isoformat())]
        analysis = {"progression": "Volume increased vs last chest day."}
        result = _validate_and_correct(analysis, today, history)
        assert result["progression"] == "Volume increased vs last chest day."

    def test_corrects_wrong_volume_distribution_groups(self):
        today = chest_day(date.today().isoformat())
        history = [
            chest_day((date.today() - timedelta(days=2)).isoformat()),
            leg_day((date.today() - timedelta(days=4)).isoformat()),
        ]
        analysis = {"volume_distribution": "Shoulders are underrepresented this week."}

        result = _validate_and_correct(analysis, today, history)

        assert result["volume_distribution"] == (
            "Legs is the most-trained and Chest is the least-trained "
            "muscle group this week."
        )

    def test_leaves_correct_volume_distribution_alone(self):
        today = chest_day(date.today().isoformat())
        history = [
            chest_day((date.today() - timedelta(days=2)).isoformat()),
            leg_day((date.today() - timedelta(days=4)).isoformat()),
        ]
        original = "legs are your most-trained group, chest is your least-trained this week."
        analysis = {"volume_distribution": original}

        result = _validate_and_correct(analysis, today, history)

        assert result["volume_distribution"] == original

    def test_does_not_touch_volume_distribution_when_window_is_empty(self):
        today = chest_day(date.today().isoformat())
        analysis = {"volume_distribution": "Shoulders are underrepresented this week."}

        result = _validate_and_correct(analysis, today, [])

        assert result["volume_distribution"] == "Shoulders are underrepresented this week."

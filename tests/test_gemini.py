"""Tests for gemini.py - LLM analysis functions."""

from gemini import build_prompt, format_workout_for_llm, mock_response


class TestBuildPrompt:
    """Tests for build_prompt function."""

    def test_prompt_contains_today_workout(self):
        """Prompt should include today's workout data."""
        today = {"title": "Chest Day", "exercises": []}
        history = []
        
        prompt = build_prompt(today, history)
        
        assert "Chest Day" in prompt

    def test_prompt_contains_history_when_provided(self):
        """Prompt should include workout history."""
        today = {"title": "Back Day", "exercises": []}
        history = [{"date": "2024-01-01", "title": "Leg Day"}]
        
        prompt = build_prompt(today, history)
        
        assert "Leg Day" in prompt

    def test_prompt_shows_no_history_message_when_empty(self):
        """Prompt should indicate when no history available."""
        today = {"title": "Arms", "exercises": []}
        history = []
        
        prompt = build_prompt(today, history)
        
        assert "No workout history available for the last 4 weeks" in prompt

    def test_prompt_contains_analysis_instructions(self):
        """Prompt should contain analysis constraints."""
        today = {"title": "Test", "exercises": []}
        history = []
        
        prompt = build_prompt(today, history)
        
        assert "Be concise and practical" in prompt
        assert "No motivational fluff" in prompt
        assert "1800 characters" in prompt

    def test_prompt_contains_required_sections(self):
        """Prompt should ask for all required analysis sections."""
        today = {"title": "Test", "exercises": []}
        history = []
        
        prompt = build_prompt(today, history)
        
        assert "Relevance to the workout plan" in prompt
        assert "Progression quality" in prompt
        assert "Good things" in prompt
        assert "Bad things" in prompt
        assert "recommendation" in prompt


class TestFormatWorkoutForLlm:
    """Tests for workout formatting helper."""

    def test_uses_alternate_exercise_name_key(self):
        workout = {
            "title": "Upper",
            "workout_perform_date": "2026-01-01",
            "exercises": [
                {"exercise_name": "Incline Press", "sets": [{"weight": 40, "reps": 12}]}
            ],
        }
        text = format_workout_for_llm(workout)
        assert "Incline Press" in text

    def test_non_numeric_set_values_render_as_zero(self):
        workout = {
            "title": "Upper",
            "workout_perform_date": "2026-01-01",
            "exercises": [
                {"excercise_name": "Row", "sets": [{"weight": "bad", "reps": "bad"}]}
            ],
        }
        text = format_workout_for_llm(workout)
        assert "0.0kg × 0 reps" in text


class TestMockResponse:
    """Tests for mock_response function."""

    def test_mock_response_returns_string(self):
        """Mock response should return a non-empty string."""
        result = mock_response({}, [])
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mock_response_contains_analysis_points(self):
        """Mock response should contain multiple analysis points."""
        result = mock_response({}, [])
        
        # Should have multiple bullet points
        assert result.count("-") >= 3

    def test_mock_response_mentions_volume(self):
        """Mock response should mention volume tracking."""
        result = mock_response({}, [])
        
        assert "volume" in result.lower() or "Volume" in result

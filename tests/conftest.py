from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_env(monkeypatch):
    """Set required environment variables for tests."""
    monkeypatch.setenv("LYFTA_API_KEY", "test_lyfta_key")
    monkeypatch.setenv("SUPABASE_DATABASE_URL", "postgresql://test:test@localhost/testdb")
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/test")
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key")


@pytest.fixture
def sample_workout():
    """Return sample Lyfta workout JSON."""
    return {
        "id": 123,
        "title": "Chest + Triceps",
        "workout_perform_date": "2025-04-23 10:00:00",
        "total_volume": 15000,
        "exercises": [
            {
                "excercise_name": "Incline Dumbbell Bench Press",
                "sets": [
                    {"weight": 30, "reps": 10},
                    {"weight": 30, "reps": 8},
                    {"weight": 30, "reps": 8}
                ]
            },
            {
                "excercise_name": "Flat DB Press",
                "sets": [
                    {"weight": 25, "reps": 12},
                    {"weight": 25, "reps": 10}
                ]
            }
        ]
    }


@pytest.fixture
def sample_workout_description():
    """Return expected transformed workout description."""
    return {
        "Incline Dumbbell Bench Press": [
            {"weight_kg": 30.0, "reps": 10},
            {"weight_kg": 30.0, "reps": 8},
            {"weight_kg": 30.0, "reps": 8}
        ],
        "Flat DB Press": [
            {"weight_kg": 25.0, "reps": 12},
            {"weight_kg": 25.0, "reps": 10}
        ]
    }


@pytest.fixture
def mock_db_connection(monkeypatch):
    """Mock database connection."""
    mock_con = MagicMock()
    mock_cur = MagicMock()
    mock_con.__enter__ = MagicMock(return_value=mock_con)
    mock_con.__exit__ = MagicMock(return_value=False)
    mock_con.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_con.cursor.return_value.__exit__ = MagicMock(return_value=False)

    return mock_con, mock_cur

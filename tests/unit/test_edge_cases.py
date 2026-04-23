from unittest.mock import MagicMock, patch

import pytest

from src.log import error, info, warn


class TestLogFunctions:
    def test_info_logs_correctly(self, capsys):
        info("test message")
        captured = capsys.readouterr()
        assert "[INFO]" in captured.out
        assert "test message" in captured.out
        assert "[2025" in captured.out or "[2026" in captured.out  # timestamp

    def test_warn_logs_correctly(self, capsys):
        warn("warning message")
        captured = capsys.readouterr()
        assert "[WARN]" in captured.out
        assert "warning message" in captured.out

    def test_error_logs_correctly(self, capsys):
        error("error message")
        captured = capsys.readouterr()
        assert "[ERROR]" in captured.out
        assert "error message" in captured.out


class TestRetryDecorator:
    def test_retry_success_first_attempt(self):
        from src.utils.retry import retry

        call_count = 0

        @retry(max_attempts=3, backoff_factor=1, initial_delay=0)
        def succeed_on_first():
            nonlocal call_count
            call_count += 1
            return "success"

        result = succeed_on_first()
        assert result == "success"
        assert call_count == 1

    def test_retry_success_later(self):
        from src.utils.retry import retry

        call_count = 0

        @retry(max_attempts=3, backoff_factor=1, initial_delay=0)
        def succeed_on_second():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("fail")
            return "success"

        result = succeed_on_second()
        assert result == "success"
        assert call_count == 2

    def test_retry_exhausted(self):
        from src.utils.retry import retry

        call_count = 0

        @retry(max_attempts=3, backoff_factor=1, initial_delay=0, exceptions=(ValueError,))
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            always_fail()
        assert call_count == 3

    def test_retry_different_exception_type(self):
        from src.utils.retry import retry

        call_count = 0

        @retry(max_attempts=3, backoff_factor=1, initial_delay=0, exceptions=(ValueError,))
        def raise_keyerror():
            nonlocal call_count
            call_count += 1
            raise KeyError("different error")

        with pytest.raises(KeyError):
            raise_keyerror()
        assert call_count == 1  # doesn't retry on different exception

    def test_retry_no_exception_param(self):
        from src.utils.retry import retry

        @retry(max_attempts=1)
        def no_exception():
            return "ok"

        result = no_exception()
        assert result == "ok"


class TestDiscordClient:
    def test_format_discord_message_with_title_and_date(self):
        from src.discord_client import format_discord_message

        workout = {
            "title": "Chest + Triceps",
            "workout_perform_date": "2025-04-23 10:00:00"
        }
        analysis = "Good workout today"

        result = format_discord_message(analysis, workout)
        assert "Chest + Triceps" in result
        assert "2025-04-23" in result
        assert "Good workout today" in result
        assert "Workout Report" in result

    def test_format_discord_message_defaults(self):
        from src.discord_client import format_discord_message

        workout = {}
        analysis = "Test"

        result = format_discord_message(analysis, workout)
        assert "Workout Report" in result
        assert "Test" in result


class TestLyftaClient:
    def test_fetch_todays_workout_returns_none_when_no_workouts(self, requests_mock):
        from src.lyfta_client import fetch_todays_workout

        requests_mock.get(
            "https://my.lyfta.app/api/v1/workouts",
            json={"workouts": []},
            status_code=200
        )

        result = fetch_todays_workout("test_key")
        assert result is None

    def test_fetch_todays_workout_returns_none_when_date_mismatch(self, requests_mock):

        from src.lyfta_client import fetch_todays_workout

        old_date = "2020-01-01"
        requests_mock.get(
            "https://my.lyfta.app/api/v1/workouts",
            json={"workouts": [{"workout_perform_date": old_date}]},
            status_code=200
        )

        result = fetch_todays_workout("test_key")
        assert result is None

    def test_fetch_todays_workout_returns_workout_when_date_matches(self, requests_mock):
        from datetime import date

        from src.lyfta_client import fetch_todays_workout

        today = date.today().isoformat()
        requests_mock.get(
            "https://my.lyfta.app/api/v1/workouts",
            json={"workouts": [{"workout_perform_date": today, "title": "Test"}]},
            status_code=200
        )

        result = fetch_todays_workout("test_key")
        assert result is not None
        assert result["title"] == "Test"


class TestDatabaseEdgeCases:
    def test_save_workout_with_minimal_data(self):
        from src.database import save_workout

        workout = {
            "workout_perform_date": "2025-04-23 10:00:00",
            "title": "Test",
            "total_volume": 1000,
            "exercises": []
        }

        with patch('src.database._get_connection') as mock_conn:
            mock_con = MagicMock()
            mock_cur = MagicMock()
            mock_con.__enter__ = MagicMock(return_value=mock_con)
            mock_con.__exit__ = MagicMock(return_value=False)
            mock_con.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
            mock_con.cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_con.cursor.return_value.__enter__.return_value.fetchone.return_value = (1, None)

            mock_conn.return_value.__enter__ = MagicMock(return_value=mock_con)
            mock_conn.return_value.__exit__ = MagicMock(return_value=False)
            mock_conn.return_value.getconn.return_value = mock_con
            mock_conn.return_value.putconn = MagicMock()

            result = save_workout(workout)
            assert result is not None


class TestGeminiClient:
    def test_mock_response_format(self):
        from src.gemini_client import mock_response

        workout = {"title": "Test"}
        history = None
        summary = None

        result = mock_response(workout, history, summary)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Volume" in result

    def test_format_summary_with_data(self):
        from src.gemini_client import _format_summary

        summary = {
            "workout_days": 4,
            "rest_days": 3,
            "avg_volume": 12000
        }
        result = _format_summary(summary)
        assert "Workout days: 4" in result
        assert "Rest days: 3" in result

    def test_format_summary_with_none(self):
        from src.gemini_client import _format_summary

        result = _format_summary(None)
        assert result == "No data"

    def test_format_summary_with_empty(self):
        from src.gemini_client import _format_summary

        result = _format_summary({})
        assert "No data" in result


class TestDataFetchEdgeCases:
    def test_fetch_today_workout_with_no_api_key(self):
        import os

        from src.data_fetch import fetch_today_workout

        original = os.environ.get("LYFTA_API_KEY")
        if "LYFTA_API_KEY" in os.environ:
            del os.environ["LYFTA_API_KEY"]

        with pytest.raises(RuntimeError, match="LYFTA_API_KEY not set"):
            fetch_today_workout()

        if original:
            os.environ["LYFTA_API_KEY"] = original


class TestPersistenceEdgeCases:
    def test_persist_today_workout_with_none(self):
        from src.persistence import persist_today_workout

        with patch('src.config.DRY_RUN', False):
            with patch('src.persistence.initialize_database') as mock_init:
                with patch('src.persistence.save_rest_day') as mock_save:
                    mock_save.return_value = None
                    result = persist_today_workout(None)
                    assert result is None
                    mock_init.assert_called_once()
                    mock_save.assert_called_once()


class TestMainEdgeCases:
    def test_rest_day_message_default(self):
        from src.main import REST_DAY_MESSAGE

        assert REST_DAY_MESSAGE == "Rest day taken. Recovery is important!"

    def test_rest_day_message_from_env(self, monkeypatch):
        monkeypatch.setenv("REST_DAY_MESSAGE", "Custom rest message")

        from importlib import reload

        import src.main
        reload(src.main)

        assert src.main.REST_DAY_MESSAGE == "Custom rest message"

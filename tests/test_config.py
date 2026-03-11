"""Tests for config.py environment parsing."""

from config import AppConfig, env_bool, env_int


def test_env_bool_true_values(monkeypatch):
    monkeypatch.setenv("TEST_FLAG", "yes")
    assert env_bool("TEST_FLAG") is True

    monkeypatch.setenv("TEST_FLAG", "TRUE")
    assert env_bool("TEST_FLAG") is True


def test_env_bool_default_when_missing(monkeypatch):
    monkeypatch.delenv("TEST_FLAG", raising=False)
    assert env_bool("TEST_FLAG", default=True) is True


def test_env_int_returns_default_on_invalid(monkeypatch):
    monkeypatch.setenv("TEST_INT", "abc")
    assert env_int("TEST_INT", 15) == 15


def test_env_int_reads_numeric_value(monkeypatch):
    monkeypatch.setenv("TEST_INT", "42")
    assert env_int("TEST_INT", 15) == 42


def test_app_config_from_env(monkeypatch):
    monkeypatch.setenv("LYFTA_ENABLED", "false")
    monkeypatch.setenv("DB_ENABLED", "1")
    monkeypatch.setenv("RETENTION_MONTHS", "6")
    monkeypatch.setenv("HISTORY_WINDOW_DAYS", "35")
    monkeypatch.setenv("LYFTA_TIMEOUT_SECONDS", "20")
    monkeypatch.setenv("DISCORD_TIMEOUT_SECONDS", "7")

    config = AppConfig.from_env()

    assert config.lyfta_enabled is False
    assert config.db_enabled is True
    assert config.retention_months == 6
    assert config.history_window_days == 35
    assert config.lyfta_timeout_seconds == 20
    assert config.discord_timeout_seconds == 7

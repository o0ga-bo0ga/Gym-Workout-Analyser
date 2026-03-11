import os
from dataclasses import dataclass


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes")


def env_int(name: str, default: int) -> int:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError:
        return default


@dataclass(frozen=True)
class AppConfig:
    lyfta_enabled: bool = True
    db_enabled: bool = True
    retention_enabled: bool = True
    analysis_enabled: bool = True
    gemini_mode: bool = True
    dry_run: bool = False
    retention_months: int = 12
    history_window_days: int = 28
    lyfta_timeout_seconds: int = 10
    discord_timeout_seconds: int = 10

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            lyfta_enabled=env_bool("LYFTA_ENABLED", True),
            db_enabled=env_bool("DB_ENABLED", True),
            retention_enabled=env_bool("RETENTION_ENABLED", True),
            analysis_enabled=env_bool("ANALYSIS_ENABLED", True),
            gemini_mode=env_bool("GEMINI_MODE", True),
            dry_run=env_bool("DRY_RUN", False),
            retention_months=env_int("RETENTION_MONTHS", 12),
            history_window_days=env_int("HISTORY_WINDOW_DAYS", 28),
            lyfta_timeout_seconds=env_int("LYFTA_TIMEOUT_SECONDS", 10),
            discord_timeout_seconds=env_int("DISCORD_TIMEOUT_SECONDS", 10),
        )


APP_CONFIG = AppConfig.from_env()

LYFTA_ENABLED: bool = APP_CONFIG.lyfta_enabled
DB_ENABLED: bool = APP_CONFIG.db_enabled
RETENTION_ENABLED: bool = APP_CONFIG.retention_enabled
ANALYSIS_ENABLED: bool = APP_CONFIG.analysis_enabled
GEMINI_MODE: bool = APP_CONFIG.gemini_mode
DRY_RUN: bool = APP_CONFIG.dry_run
RETENTION_MONTHS: int = APP_CONFIG.retention_months
HISTORY_WINDOW_DAYS: int = APP_CONFIG.history_window_days
LYFTA_TIMEOUT_SECONDS: int = APP_CONFIG.lyfta_timeout_seconds
DISCORD_TIMEOUT_SECONDS: int = APP_CONFIG.discord_timeout_seconds

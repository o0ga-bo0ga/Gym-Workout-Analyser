import os


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes")


LYFTA_ENABLED: bool = env_bool("LYFTA_ENABLED", True)
DATABASE_ENABLED: bool = env_bool("DATABASE_ENABLED", True)
RETENTION_ENABLED: bool = env_bool("RETENTION_ENABLED", True)
ANALYSIS_ENABLED: bool = env_bool("ANALYSIS_ENABLED", True)
DRY_RUN: bool = env_bool("DRY_RUN", False)

LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "groq").lower()
LLM_MODEL: str = os.environ.get("LLM_MODEL", "llama-3.1-8b-instant")
LLM_ENABLED: bool = LLM_PROVIDER == "groq"
LLM_MOCK: bool = env_bool("LLM_MOCK", False)

TONE: str = os.environ.get("TONE", "balanced").lower()

# Backfill / rerun controls
BACKFILL_DATE: str | None = os.environ.get("BACKFILL_DATE") or None
SKIP_DB_SAVE: bool = env_bool("SKIP_DB_SAVE", False)

# LangSmith config
LANGSMITH_ENABLED: bool = env_bool("LANGSMITH_ENABLED", True)

# Backward compatibility alias
DB_ENABLED: bool = DATABASE_ENABLED
GEMINI_MODE: bool = LLM_MOCK

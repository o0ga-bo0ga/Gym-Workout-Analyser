import os


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes")

LYFTA_ENABLED: bool = env_bool("LYFTA_ENABLED", True)
DATABASE_ENABLED: bool = env_bool("DATABASE_ENABLED", True)
RETENTION_ENABLED: bool = env_bool("RETENTION_ENABLED", True)
ANALYSIS_ENABLED: bool = env_bool("ANALYSIS_ENABLED", True)
GEMINI_MODE: bool = env_bool("GEMINI_MODE", True)
DRY_RUN: bool = env_bool("DRY_RUN", False)

# Backward compatibility alias
DB_ENABLED: bool = DATABASE_ENABLED

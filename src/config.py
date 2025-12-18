import os

def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes")

LYFTA_ENABLED = env_bool("LYFTA_ENABLED", True)
DB_ENABLED = env_bool("DB_ENABLED", True)
RETENTION_ENABLED = env_bool("RETENTION_ENABLED", True)
ANALYSIS_ENABLED = env_bool("ANALYSIS_ENABLED", True)  # Gemini later
GEMINI_MODE = env_bool("GEMINI_MODE", "real")  # "real" or "mock"
DRY_RUN = env_bool("DRY_RUN", False)
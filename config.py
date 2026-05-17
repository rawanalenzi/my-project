"""Application configuration and filesystem paths."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Runtime data (forensics + SOC state)
LOGS_DIR = os.path.join(BASE_DIR, "logs")
ATTACKS_LOG_FILE = os.path.join(LOGS_DIR, "attacks_log.txt")
SOC_STATE_FILE = os.path.join(LOGS_DIR, "soc_state.json")

# Legacy paths (migrated on startup if present)
LEGACY_ATTACKS_LOG = os.path.join(BASE_DIR, "attacks_log.txt")
LEGACY_SOC_STATE = os.path.join(BASE_DIR, "soc_state.json")

# Flask
SECRET_KEY = os.environ.get("HONEYGATE_SECRET_KEY", "honeygate_pro_2026")

# Real operator — only account with SOC + legitimate session
REAL_ADMIN_EMAIL = "admin@bank.com"
REAL_ADMIN_PASSWORD = "123456"

# Decoy credential pairs (logged as intelligence; still get fake success UX)
DECOY_CREDENTIALS = {
    (REAL_ADMIN_EMAIL, "admin123"),
    ("backup@bank.com", REAL_ADMIN_PASSWORD),
}

ROLE_ADMIN = "admin"
ROLE_DECOY = "decoy"


def ensure_runtime_dirs():
    """Create logs directory and migrate legacy log files if needed."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    for legacy, target in (
        (LEGACY_ATTACKS_LOG, ATTACKS_LOG_FILE),
        (LEGACY_SOC_STATE, SOC_STATE_FILE),
    ):
        if os.path.isfile(legacy) and not os.path.isfile(target):
            os.replace(legacy, target)

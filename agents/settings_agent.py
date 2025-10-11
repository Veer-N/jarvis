import json
from pathlib import Path
from cryptography.fernet import Fernet

# -------------------------------
# Config
# -------------------------------
DATA_DIR = Path("data")
SETTINGS_FILE = DATA_DIR / "settings.json"
KEY_FILE = DATA_DIR / "secret.key"

# -------------------------------
# Key Management
# -------------------------------
def get_or_create_key():
    """Create or load encryption key."""
    if not KEY_FILE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
    else:
        key = KEY_FILE.read_bytes()
    return Fernet(key)

fernet = get_or_create_key()

# -------------------------------
# Settings Load / Save
# -------------------------------
def load_settings():
    """Load settings from JSON file (create default if missing)."""
    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_settings = {
            "aws": {"enabled": False, "access_key": "", "secret_key": ""},
            "jira": {"enabled": False, "username": "", "api_token": ""},
            "docker": {"enabled": False, "host": ""}
        }
        save_settings(default_settings)
        return default_settings

    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(settings: dict):
    """Save settings to JSON file."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

# -------------------------------
# Encryption helpers
# -------------------------------
def encrypt(text: str) -> str:
    if not text:
        return ""
    return fernet.encrypt(text.encode()).decode()

def decrypt(token: str) -> str:
    if not token:
        return ""
    return fernet.decrypt(token.encode()).decode()

# -------------------------------
# High-level Accessors
# -------------------------------
def get_setting(section: str):
    """Get settings for a given section (aws/jira/docker)."""
    settings = load_settings()
    return settings.get(section, {})

def update_setting(section: str, data: dict):
    """Update settings for a section and persist them."""
    settings = load_settings()
    settings[section] = data
    save_settings(settings)

# -------------------------------
# Service toggle helpers (used by UI)
# -------------------------------
def get_service_status(service: str) -> bool:
    """Return whether a service (aws/jira/docker) is enabled."""
    settings = load_settings()
    return settings.get(service, {}).get("enabled", False)

def set_service_status(service: str, enabled: bool):
    """Enable or disable a service and persist."""
    settings = load_settings()
    if service not in settings:
        settings[service] = {}
    settings[service]["enabled"] = enabled
    save_settings(settings)

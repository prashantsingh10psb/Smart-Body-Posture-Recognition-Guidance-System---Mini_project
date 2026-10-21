"""
System Configuration & Settings
Smart Body Posture Recognition & Guidance System
"""

import os
from pathlib import Path
from typing import Dict, Any
import json

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Server configs
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Authentication key for kiosk device sensor-trigger API (as per Section 10.2 / 14.1)
DEVICE_KEY = os.getenv("DEVICE_KEY", "kiosk-device-secret-key-2026")

# Database
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(DATA_DIR / "kiosk_posture.db")))

# Posture & Feedback parameters
HOLD_DURATION_SECONDS = float(os.getenv("HOLD_DURATION_SECONDS", "2.5"))
ERROR_AUDIO_DELAY_SECONDS = float(os.getenv("ERROR_AUDIO_DELAY_SECONDS", "2.0"))
TARGET_FPS = int(os.getenv("TARGET_FPS", "20"))
LATENCY_SLA_MS = 300.0  # From NFR table: p95 latency <= 300 ms

# TTS
TTS_ENABLED = os.getenv("TTS_ENABLED", "True").lower() in ("true", "1", "yes")
TTS_RATE = int(os.getenv("TTS_RATE", "165"))
TTS_VOLUME = float(os.getenv("TTS_VOLUME", "0.9"))

# Posture Rules Path
POSTURE_RULES_FILE = CONFIG_DIR / "posture_rules.json"


def load_posture_rules() -> Dict[str, Any]:
    """Loads the posture rule definitions from the JSON configuration."""
    if not POSTURE_RULES_FILE.exists():
        raise FileNotFoundError(f"Posture rules file not found: {POSTURE_RULES_FILE}")
    with open(POSTURE_RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_posture_rules(data: Dict[str, Any]) -> None:
    """Saves updated posture rule definitions to the JSON configuration."""
    with open(POSTURE_RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

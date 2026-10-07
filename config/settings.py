"""Read optional local settings without mixing configuration into tests."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)


def positive_integer_setting(name: str, default: int) -> int:
    """Reject a typo early, with the setting name in the error."""
    value = int(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return value


@dataclass(frozen=True)
class Settings:
    app_start_timeout_ms: int
    action_timeout_ms: int
    assertion_timeout_ms: int


settings = Settings(
    app_start_timeout_ms=positive_integer_setting("APP_START_TIMEOUT_MS", 10000),
    action_timeout_ms=positive_integer_setting("ACTION_TIMEOUT_MS", 5000),
    assertion_timeout_ms=positive_integer_setting("ASSERTION_TIMEOUT_MS", 5000),
)

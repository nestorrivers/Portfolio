from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final


def _get_env(name: str, default: str) -> str:
    """
    Read an environment variable with a default.
    Centralising this avoids scattered os.getenv calls.
    """
    return os.getenv(name, default)


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer") from exc


def _get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppConfig:
    """
    Application-wide configuration.

    This object is immutable by design.
    It should be constructed once and passed around or imported.
    """

    env: str
    log_level: str

    http_timeout: int
    http_retries: int
    http_backoff: float


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.
    Defaults are intentionally conservative.
    """

    return AppConfig(
        env=_get_env("PUBLIC_DATA_ENV", "development"),
        log_level=_get_env("PUBLIC_DATA_LOG_LEVEL", "INFO"),
        http_timeout=_get_int_env("PUBLIC_DATA_HTTP_TIMEOUT", 10),
        http_retries=_get_int_env("PUBLIC_DATA_HTTP_RETRIES", 3),
        http_backoff=float(
            _get_env("PUBLIC_DATA_HTTP_BACKOFF", "0.5")
        ),
    )


# Singleton-style config instance.
# Import this where needed; do not re-load config ad hoc.
CONFIG: Final[AppConfig] = load_config()

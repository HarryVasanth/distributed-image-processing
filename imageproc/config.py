"""Runtime configuration, read once from the environment."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_BROKER_URL = "amqp://guest:guest@localhost:5672//"
DEFAULT_RESULT_BACKEND = "redis://localhost:6379/0"


def _value(env: Mapping[str, str], name: str, default: str) -> str:
    raw = env.get(name)
    return default if raw is None or raw.strip() == "" else raw.strip()


def _positive_int(env: Mapping[str, str], name: str, default: int) -> int:
    raw = env.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero, got {value}")
    return value


def _positive_float(env: Mapping[str, str], name: str, default: float) -> float:
    raw = env.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number, got {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero, got {value}")
    return value


@dataclass(frozen=True)
class Settings:
    """Cluster settings shared by the client and the workers."""

    broker_url: str
    result_backend: str
    flower_url: str | None
    chunks: int
    poll_interval: float
    task_timeout: float
    max_payload_bytes: int


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build settings from environment variables.

    Raises:
        ValueError: if a numeric variable cannot be parsed or is out of range.
    """
    env = os.environ if env is None else env
    flower_url = _value(env, "IMAGEPROC_FLOWER_URL", "")
    return Settings(
        broker_url=_value(env, "IMAGEPROC_BROKER_URL", DEFAULT_BROKER_URL),
        result_backend=_value(env, "IMAGEPROC_RESULT_BACKEND", DEFAULT_RESULT_BACKEND),
        flower_url=flower_url or None,
        chunks=_positive_int(env, "IMAGEPROC_CHUNKS", 8),
        poll_interval=_positive_float(env, "IMAGEPROC_POLL_INTERVAL", 0.5),
        task_timeout=_positive_float(env, "IMAGEPROC_TASK_TIMEOUT", 600.0),
        max_payload_bytes=_positive_int(env, "IMAGEPROC_MAX_PAYLOAD_BYTES", 64 * 1024 * 1024),
    )


settings = load_settings()

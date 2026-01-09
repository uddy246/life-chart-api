from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, ValidationError


class Settings(BaseModel):
    ENV: Literal["dev", "test", "prod"] = "dev"
    RATE_LIMIT_PER_MIN: int = 60
    LOG_LEVEL: str = "INFO"
    MAX_FORECAST_RANGE_MONTHS: int = 60
    MAX_TIMELINE_RANGE_MONTHS: int = 60
    MAX_RANGE_QUARTERS: int = 80


def _env_value(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)


def _detect_env(default: str) -> str:
    if "PYTEST_CURRENT_TEST" in os.environ:
        return "test"
    return default


def load_settings() -> Settings:
    raw = {
        "ENV": _detect_env(_env_value("ENV", "dev")),
        "RATE_LIMIT_PER_MIN": _env_value("RATE_LIMIT_PER_MIN", "60"),
        "LOG_LEVEL": _env_value("LOG_LEVEL", "INFO"),
        "MAX_FORECAST_RANGE_MONTHS": _env_value("MAX_FORECAST_RANGE_MONTHS", "60"),
        "MAX_TIMELINE_RANGE_MONTHS": _env_value("MAX_TIMELINE_RANGE_MONTHS", "60"),
        "MAX_RANGE_QUARTERS": _env_value("MAX_RANGE_QUARTERS", "80"),
    }

    def to_int(value: str, field: str) -> int:
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"{field} must be an integer") from exc

    try:
        parsed = {
            "ENV": raw["ENV"],
            "RATE_LIMIT_PER_MIN": to_int(raw["RATE_LIMIT_PER_MIN"], "RATE_LIMIT_PER_MIN"),
            "LOG_LEVEL": raw["LOG_LEVEL"],
            "MAX_FORECAST_RANGE_MONTHS": to_int(raw["MAX_FORECAST_RANGE_MONTHS"], "MAX_FORECAST_RANGE_MONTHS"),
            "MAX_TIMELINE_RANGE_MONTHS": to_int(raw["MAX_TIMELINE_RANGE_MONTHS"], "MAX_TIMELINE_RANGE_MONTHS"),
            "MAX_RANGE_QUARTERS": to_int(raw["MAX_RANGE_QUARTERS"], "MAX_RANGE_QUARTERS"),
        }
    except ValueError as exc:
        raise RuntimeError(f"Invalid settings: {exc}") from exc

    if parsed["ENV"] == "test":
        parsed["RATE_LIMIT_PER_MIN"] = max(parsed["RATE_LIMIT_PER_MIN"], 1000)

    try:
        return Settings(**parsed)
    except ValidationError as exc:
        raise RuntimeError(f"Invalid settings: {exc}") from exc


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()

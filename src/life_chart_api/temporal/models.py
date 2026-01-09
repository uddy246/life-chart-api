from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from hashlib import sha1
from typing import Any


@dataclass(frozen=True)
class Cycle:
    cycleId: str
    system: str
    kind: str
    domain: str
    themes: list[str]
    start: str
    end: str
    intensity: float
    polarity: str
    evidence: list[dict[str, Any]]
    peak: str | None = None
    ageStart: float | None = None
    ageEnd: float | None = None
    notes: list[str] | None = None


def normalize_iso_ym(value: date | datetime | str) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m")
    if isinstance(value, date):
        return value.strftime("%Y-%m")
    if isinstance(value, str):
        if len(value) == 7:
            return value
        if len(value) == 10:
            return value[:7]
        parsed = datetime.fromisoformat(value)
        return parsed.strftime("%Y-%m")
    raise TypeError("normalize_iso_ym expects date, datetime, or str")


def normalize_iso_ymd(value: date | datetime | str) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str):
        if len(value) == 10:
            return value
        parsed = datetime.fromisoformat(value)
        return parsed.strftime("%Y-%m-%d")
    raise TypeError("normalize_iso_ymd expects date, datetime, or str")


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def stable_id(parts: list[str]) -> str:
    raw = "|".join(parts)
    digest = sha1(raw.encode("utf-8")).hexdigest()[:12]
    return f"cycle-{digest}"


def sort_cycles(cycles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def sort_key(cycle: dict[str, Any]) -> tuple:
        return (
            cycle.get("start", ""),
            cycle.get("end", ""),
            cycle.get("system", ""),
            cycle.get("cycleId", ""),
        )

    return sorted(cycles, key=sort_key)

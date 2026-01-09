from __future__ import annotations

from typing import Any

_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]
_SIGN_MAP = {name.lower(): name for name in _SIGNS}
_LORDS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"}


def _normalize_sign(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = _SIGN_MAP.get(value.strip().lower())
    return normalized


def _normalize_lord(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if stripped in _LORDS:
        return stripped
    return None


def _get_computed_value(computed: Any, key: str) -> Any:
    if isinstance(computed, dict):
        return computed.get(key)
    return getattr(computed, key, None)


def overlay_vedic_tier1(vedic_template: dict[str, Any], computed: Any) -> dict[str, Any]:
    lagna_sign = _normalize_sign(_get_computed_value(computed, "lagna_sign"))
    moon_sign = _normalize_sign(_get_computed_value(computed, "moon_sign"))
    lagna_lord = _normalize_lord(_get_computed_value(computed, "lagna_lord"))

    if lagna_sign:
        vedic_template["lagna_sign"] = lagna_sign
    if moon_sign:
        vedic_template["moon_sign"] = moon_sign
    if lagna_lord:
        vedic_template["lagna_lord"] = lagna_lord

    return vedic_template

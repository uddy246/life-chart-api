from __future__ import annotations

from typing import Any

_SIGN_ENUM = {
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
}


def _normalize_sign(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    lowered = value.strip().lower()
    if lowered in _SIGN_ENUM:
        return lowered
    return None


def _get_computed_value(computed: Any, key: str) -> Any:
    if isinstance(computed, dict):
        return computed.get(key)
    return getattr(computed, key, None)


def _set_identity_sign(western: dict[str, Any], key: str, value: str) -> None:
    identity = western.get("identity")
    if not isinstance(identity, dict):
        return
    placement = identity.get(key)
    if not isinstance(placement, dict):
        return
    placement["sign"] = value


def _set_planet_sign(western: dict[str, Any], planet_name: str, value: str) -> None:
    planets = western.get("planets")
    if not isinstance(planets, list):
        return
    for planet in planets:
        if isinstance(planet, dict) and planet.get("planet") == planet_name:
            planet["sign"] = value
            return


def overlay_western_tier1(western_template: dict[str, Any], computed: Any) -> dict[str, Any]:
    sun_sign = _normalize_sign(_get_computed_value(computed, "sun_sign"))
    moon_sign = _normalize_sign(_get_computed_value(computed, "moon_sign"))
    asc_sign = _normalize_sign(_get_computed_value(computed, "ascendant_sign"))

    if sun_sign:
        _set_identity_sign(western_template, "sunSign", sun_sign)
        _set_planet_sign(western_template, "sun", sun_sign)
    if moon_sign:
        _set_identity_sign(western_template, "moonSign", moon_sign)
        _set_planet_sign(western_template, "moon", moon_sign)
    if asc_sign:
        _set_identity_sign(western_template, "ascendant", asc_sign)

    return western_template

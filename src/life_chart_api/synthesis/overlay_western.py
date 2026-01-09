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

_MERCURY_STYLE_TO_SIGN = {
    "Direct and candid": "aries",
    "Practical and steady": "taurus",
    "Quick and curious": "gemini",
    "Reflective and cautious": "cancer",
    "Confident and warm": "leo",
    "Precise and analytical": "virgo",
    "Diplomatic and balanced": "libra",
    "Intense and probing": "scorpio",
    "Big-picture and candid": "sagittarius",
    "Measured and strategic": "capricorn",
    "Inventive and detached": "aquarius",
    "Intuitive and poetic": "pisces",
}

_VENUS_STYLE_TO_SIGN = {
    "Bold and spontaneous": "aries",
    "Sensual and steady": "taurus",
    "Playful and verbal": "gemini",
    "Protective and loyal": "cancer",
    "Warm and demonstrative": "leo",
    "Devoted and practical": "virgo",
    "Harmonious and refined": "libra",
    "All-in and magnetic": "scorpio",
    "Adventurous and open": "sagittarius",
    "Committed and reserved": "capricorn",
    "Independent and unconventional": "aquarius",
    "Romantic and empathetic": "pisces",
}

_MARS_STYLE_TO_SIGN = {
    "Decisive and direct": "aries",
    "Persistent and steady": "taurus",
    "Restless and adaptable": "gemini",
    "Protective and reactive": "cancer",
    "Bold and expressive": "leo",
    "Methodical and precise": "virgo",
    "Tactical and measured": "libra",
    "Intense and relentless": "scorpio",
    "Adventurous and blunt": "sagittarius",
    "Disciplined and patient": "capricorn",
    "Innovative and detached": "aquarius",
    "Subtle and fluid": "pisces",
}

_SATURN_THEME_TO_SIGN = {
    "Discipline through initiative": "aries",
    "Patience through stability": "taurus",
    "Focus through clarity": "gemini",
    "Boundaries through care": "cancer",
    "Leadership through responsibility": "leo",
    "Service through refinement": "virgo",
    "Commitment through balance": "libra",
    "Depth through endurance": "scorpio",
    "Wisdom through limits": "sagittarius",
    "Mastery through structure": "capricorn",
    "Duty through principles": "aquarius",
    "Compassion through boundaries": "pisces",
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


def overlay_western_tier2(western_template: dict[str, Any], computed: Any) -> dict[str, Any]:
    mercury_sign = _normalize_sign(_get_computed_value(computed, "mercury_sign"))
    venus_sign = _normalize_sign(_get_computed_value(computed, "venus_sign"))
    mars_sign = _normalize_sign(_get_computed_value(computed, "mars_sign"))
    saturn_sign = _normalize_sign(_get_computed_value(computed, "saturn_sign"))

    if not mercury_sign:
        mercury_style = _get_computed_value(computed, "mercury_style")
        if isinstance(mercury_style, str):
            mercury_sign = _MERCURY_STYLE_TO_SIGN.get(mercury_style)
    if not venus_sign:
        venus_style = _get_computed_value(computed, "venus_style")
        if isinstance(venus_style, str):
            venus_sign = _VENUS_STYLE_TO_SIGN.get(venus_style)
    if not mars_sign:
        mars_style = _get_computed_value(computed, "mars_style")
        if isinstance(mars_style, str):
            mars_sign = _MARS_STYLE_TO_SIGN.get(mars_style)
    if not saturn_sign:
        saturn_theme = _get_computed_value(computed, "saturn_theme")
        if isinstance(saturn_theme, str):
            saturn_sign = _SATURN_THEME_TO_SIGN.get(saturn_theme)

    if mercury_sign:
        _set_planet_sign(western_template, "mercury", mercury_sign)
    if venus_sign:
        _set_planet_sign(western_template, "venus", venus_sign)
    if mars_sign:
        _set_planet_sign(western_template, "mars", mars_sign)
    if saturn_sign:
        _set_planet_sign(western_template, "saturn", saturn_sign)

    return western_template

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from life_chart_api.astrology.western.types import WesternChartFeatures

_SIGN_NAMES = [
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

_ELEMENT_BY_SIGN = {
    "Aries": "Fire",
    "Leo": "Fire",
    "Sagittarius": "Fire",
    "Taurus": "Earth",
    "Virgo": "Earth",
    "Capricorn": "Earth",
    "Gemini": "Air",
    "Libra": "Air",
    "Aquarius": "Air",
    "Cancer": "Water",
    "Scorpio": "Water",
    "Pisces": "Water",
}

_MODALITY_BY_SIGN = {
    "Aries": "Cardinal",
    "Cancer": "Cardinal",
    "Libra": "Cardinal",
    "Capricorn": "Cardinal",
    "Taurus": "Fixed",
    "Leo": "Fixed",
    "Scorpio": "Fixed",
    "Aquarius": "Fixed",
    "Gemini": "Mutable",
    "Virgo": "Mutable",
    "Sagittarius": "Mutable",
    "Pisces": "Mutable",
}

_MERCURY_STYLE_MAP = {
    "Aries": "Direct and candid",
    "Taurus": "Practical and steady",
    "Gemini": "Quick and curious",
    "Cancer": "Reflective and cautious",
    "Leo": "Confident and warm",
    "Virgo": "Precise and analytical",
    "Libra": "Diplomatic and balanced",
    "Scorpio": "Intense and probing",
    "Sagittarius": "Big-picture and candid",
    "Capricorn": "Measured and strategic",
    "Aquarius": "Inventive and detached",
    "Pisces": "Intuitive and poetic",
}

_VENUS_STYLE_MAP = {
    "Aries": "Bold and spontaneous",
    "Taurus": "Sensual and steady",
    "Gemini": "Playful and verbal",
    "Cancer": "Protective and loyal",
    "Leo": "Warm and demonstrative",
    "Virgo": "Devoted and practical",
    "Libra": "Harmonious and refined",
    "Scorpio": "All-in and magnetic",
    "Sagittarius": "Adventurous and open",
    "Capricorn": "Committed and reserved",
    "Aquarius": "Independent and unconventional",
    "Pisces": "Romantic and empathetic",
}

_MARS_STYLE_MAP = {
    "Aries": "Decisive and direct",
    "Taurus": "Persistent and steady",
    "Gemini": "Restless and adaptable",
    "Cancer": "Protective and reactive",
    "Leo": "Bold and expressive",
    "Virgo": "Methodical and precise",
    "Libra": "Tactical and measured",
    "Scorpio": "Intense and relentless",
    "Sagittarius": "Adventurous and blunt",
    "Capricorn": "Disciplined and patient",
    "Aquarius": "Innovative and detached",
    "Pisces": "Subtle and fluid",
}

_SATURN_THEME_MAP = {
    "Aries": "Discipline through initiative",
    "Taurus": "Patience through stability",
    "Gemini": "Focus through clarity",
    "Cancer": "Boundaries through care",
    "Leo": "Leadership through responsibility",
    "Virgo": "Service through refinement",
    "Libra": "Commitment through balance",
    "Scorpio": "Depth through endurance",
    "Sagittarius": "Wisdom through limits",
    "Capricorn": "Mastery through structure",
    "Aquarius": "Duty through principles",
    "Pisces": "Compassion through boundaries",
}


def _normalize_time(time_str: str) -> str:
    parts = time_str.split(":")
    if len(parts) == 2:
        return f"{time_str}:00"
    if len(parts) == 3:
        return time_str
    raise ValueError("time must be HH:MM or HH:MM:SS")


def _to_utc(date_str: str, time_str: str, tz_name: str) -> datetime:
    normalized_time = _normalize_time(time_str)
    try:
        tzinfo = ZoneInfo(tz_name)
    except Exception as exc:
        raise ValueError(f"Invalid timezone: {tz_name}") from exc
    local_dt = datetime.strptime(
        f"{date_str} {normalized_time}", "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=tzinfo)
    return local_dt.astimezone(timezone.utc)


def _julian_day(utc_dt: datetime) -> float:
    hour_decimal = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + utc_dt.microsecond / 3_600_000_000.0
    )
    return swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        hour_decimal,
        swe.GREG_CAL,
    )


def _longitude_for(jd_ut: float, planet_id: int) -> float:
    values, _ = swe.calc_ut(jd_ut, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    return values[0] % 360.0


def _sign_from_longitude(lon: float) -> str:
    return _SIGN_NAMES[int(lon // 30) % 12]


def _ascendant_longitude(jd_ut: float, lat: float, lon: float) -> float:
    try:
        _, ascmc = swe.houses_ex(jd_ut, lat, lon, b"P")
    except Exception:
        _, ascmc = swe.houses(jd_ut, lat, lon, b"P")
    return ascmc[0] % 360.0


def _dominant_from_signs(signs: list[str], mapping: dict[str, str]) -> str | None:
    counts: dict[str, int] = {}
    for sign in signs:
        key = mapping[sign]
        counts[key] = counts.get(key, 0) + 1
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    if len(sorted_counts) < 2:
        return sorted_counts[0][0]
    if sorted_counts[0][1] == sorted_counts[1][1]:
        return None
    return sorted_counts[0][0]


def _whole_sign_notes(asc_sign: str) -> list[str]:
    start_index = _SIGN_NAMES.index(asc_sign)
    signs = [
        _SIGN_NAMES[(start_index + offset) % 12] for offset in range(len(_SIGN_NAMES))
    ]
    return [f"House {idx + 1}: {sign}" for idx, sign in enumerate(signs)]


def compute_western_features(
    date: str, time: str, tz: str, lat: float, lon: float
) -> WesternChartFeatures:
    utc_dt = _to_utc(date, time, tz)
    jd_ut = _julian_day(utc_dt)

    sun_sign = _sign_from_longitude(_longitude_for(jd_ut, swe.SUN))
    moon_sign = _sign_from_longitude(_longitude_for(jd_ut, swe.MOON))
    mercury_sign = _sign_from_longitude(_longitude_for(jd_ut, swe.MERCURY))
    venus_sign = _sign_from_longitude(_longitude_for(jd_ut, swe.VENUS))
    mars_sign = _sign_from_longitude(_longitude_for(jd_ut, swe.MARS))
    saturn_sign = _sign_from_longitude(_longitude_for(jd_ut, swe.SATURN))
    asc_sign = _sign_from_longitude(_ascendant_longitude(jd_ut, lat, lon))

    dominant_element = _dominant_from_signs(
        [sun_sign, moon_sign, asc_sign], _ELEMENT_BY_SIGN
    )
    dominant_modality = _dominant_from_signs(
        [sun_sign, moon_sign, asc_sign], _MODALITY_BY_SIGN
    )

    return WesternChartFeatures(
        sun_sign=sun_sign,
        moon_sign=moon_sign,
        ascendant_sign=asc_sign,
        dominant_element=dominant_element,
        dominant_modality=dominant_modality,
        mercury_style=_MERCURY_STYLE_MAP.get(mercury_sign, "Balanced and observant"),
        mars_style=_MARS_STYLE_MAP.get(mars_sign, "Measured and steady"),
        venus_style=_VENUS_STYLE_MAP.get(venus_sign, "Warm and sincere"),
        saturn_theme=_SATURN_THEME_MAP.get(saturn_sign, "Responsibility through limits"),
        notes=_whole_sign_notes(asc_sign),
    )

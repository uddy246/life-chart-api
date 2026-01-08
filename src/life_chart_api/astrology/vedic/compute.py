from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import swisseph as swe

from life_chart_api.astrology.vedic.types import VedicChartFeatures

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

_SIGN_LORDS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
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


def setup_swe(ephe_path: str | None = None, sid_mode: int = swe.SIDM_LAHIRI) -> None:
    if ephe_path:
        swe.set_ephe_path(ephe_path)
    swe.set_sid_mode(sid_mode)


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


def _julday_ut(dt_utc: datetime) -> float:
    hour_decimal = (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
        + dt_utc.microsecond / 3_600_000_000.0
    )
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        hour_decimal,
        swe.GREG_CAL,
    )


def _norm360(value: float) -> float:
    return value % 360.0


def _sign_index_from_lon(lon: float) -> int:
    return int(lon // 30) % 12


def _deg_in_sign(lon: float) -> float:
    return lon % 30.0


def _nakshatra_from_lon(lon: float) -> tuple[int, int]:
    segment = 360.0 / 27.0
    pada_size = segment / 4.0
    nak_index = int(lon // segment) + 1
    offset = lon % segment
    pada = int(offset // pada_size) + 1
    return nak_index, pada


def _whole_sign_house(asc_sign_index: int, planet_sign_index: int) -> int:
    return ((planet_sign_index - asc_sign_index) % 12) + 1


def _calc_lon_ut(jd_ut: float, body: int) -> tuple[float, float]:
    values, _ = swe.calc_ut(jd_ut, body, swe.FLG_SWIEPH | swe.FLG_SPEED)
    return values[0], values[3]


def _ascendant_longitude(jd_ut: float, lat: float, lon: float) -> float:
    try:
        _, ascmc = swe.houses_ex(jd_ut, lat, lon, b"P", swe.FLG_SIDEREAL)
    except Exception:
        _, ascmc = swe.houses(jd_ut, lat, lon, b"P")
    return ascmc[0]


def _planet_placements(
    jd_ut: float, ayanamsa: float, asc_sign_index: int
) -> dict[str, dict[str, float | int | bool]]:
    bodies = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE,
    }

    placements: dict[str, dict[str, float | int | bool]] = {}
    for name, body in bodies.items():
        lon_trop, speed = _calc_lon_ut(jd_ut, body)
        lon_sid = _norm360(lon_trop - ayanamsa)
        sign_index = _sign_index_from_lon(lon_sid)
        house = _whole_sign_house(asc_sign_index, sign_index)
        nak_index, pada = _nakshatra_from_lon(lon_sid)
        placements[name] = {
            "lon": lon_sid,
            "sign_index": sign_index,
            "deg_in_sign": _deg_in_sign(lon_sid),
            "house": house,
            "nakshatra": nak_index,
            "pada": pada,
            "retrograde": speed < 0,
        }

    rahu_lon = float(placements["Rahu"]["lon"])
    ketu_lon = _norm360(rahu_lon + 180.0)
    ketu_sign_index = _sign_index_from_lon(ketu_lon)
    ketu_house = _whole_sign_house(asc_sign_index, ketu_sign_index)
    ketu_nak, ketu_pada = _nakshatra_from_lon(ketu_lon)
    placements["Ketu"] = {
        "lon": ketu_lon,
        "sign_index": ketu_sign_index,
        "deg_in_sign": _deg_in_sign(ketu_lon),
        "house": ketu_house,
        "nakshatra": ketu_nak,
        "pada": ketu_pada,
        "retrograde": True,
    }

    return placements


def compute_vedic_features(
    date: str,
    time: str,
    tz: str,
    lat: float,
    lon: float,
    utc_dt: datetime | None = None,
    ephe_path: str | None = None,
) -> VedicChartFeatures:
    setup_swe(ephe_path)

    if utc_dt is None:
        utc_dt = _to_utc(date, time, tz)
    else:
        if utc_dt.tzinfo is None:
            raise ValueError("utc_dt must be timezone-aware")
        utc_dt = utc_dt.astimezone(timezone.utc)

    jd_ut = _julday_ut(utc_dt)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    asc_lon = _norm360(_ascendant_longitude(jd_ut, lat, lon))
    asc_sign_index = _sign_index_from_lon(asc_lon)
    asc_sign = _SIGN_NAMES[asc_sign_index]

    placements = _planet_placements(jd_ut, ayanamsa, asc_sign_index)

    moon_sign = _SIGN_NAMES[int(placements["Moon"]["sign_index"])]
    lagna_lord = _SIGN_LORDS.get(asc_sign)

    moon_afflicted = int(placements["Moon"]["sign_index"]) in {
        int(placements["Saturn"]["sign_index"]),
        int(placements["Mars"]["sign_index"]),
        int(placements["Rahu"]["sign_index"]),
        int(placements["Ketu"]["sign_index"]),
    }

    saturn_sign = _SIGN_NAMES[int(placements["Saturn"]["sign_index"])]
    saturn_theme = _SATURN_THEME_MAP.get(
        saturn_sign,
        "Responsibility through structure",
    )

    rahu_house = int(placements["Rahu"]["house"])
    ketu_house = int(placements["Ketu"]["house"])
    rahu_ketu_emphasis = (
        rahu_house in {1, 4, 7, 10}
        or ketu_house in {1, 4, 7, 10}
        or int(placements["Rahu"]["sign_index"]) == asc_sign_index
        or int(placements["Ketu"]["sign_index"]) == asc_sign_index
        or int(placements["Rahu"]["sign_index"])
        == int(placements["Moon"]["sign_index"])
        or int(placements["Ketu"]["sign_index"])
        == int(placements["Moon"]["sign_index"])
    )

    return VedicChartFeatures(
        lagna_sign=asc_sign,
        lagna_lord=lagna_lord,
        moon_sign=moon_sign,
        moon_afflicted=moon_afflicted,
        saturn_theme=saturn_theme,
        rahu_ketu_emphasis=rahu_ketu_emphasis,
        life_direction_hint=None,
        timing_sensitivity_hint=None,
        current_phase_hint=None,
        notes=[],
    )

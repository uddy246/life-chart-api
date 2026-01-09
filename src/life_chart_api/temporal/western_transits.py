from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import swisseph as swe

from life_chart_api.temporal.models import clamp01, normalize_iso_ym, sort_cycles, stable_id

_ORB_RETURN = 2.0
_ORB_SATURN_ASPECT = 1.5

_ASPECTS = {
    "conjunction": 0.0,
    "square": 90.0,
    "opposition": 180.0,
}

_EVENT_THEMES = {
    "return_saturn": ["saturn_return", "discipline", "responsibility"],
    "return_jupiter": ["jupiter_return", "expansion", "growth"],
    "transit_saturn_aspect": ["saturn_transit", "pressure", "structure"],
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
    tzinfo = ZoneInfo(tz_name)
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


def _planet_longitude(dt_utc: datetime, planet_id: int) -> float:
    jd_ut = _julday_ut(dt_utc)
    values, _ = swe.calc_ut(jd_ut, planet_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    return values[0] % 360.0


def _ascendant_longitude(dt_utc: datetime, lat: float, lon: float) -> float:
    jd_ut = _julday_ut(dt_utc)
    try:
        _, ascmc = swe.houses_ex(jd_ut, lat, lon, b"P")
    except Exception:
        _, ascmc = swe.houses(jd_ut, lat, lon, b"P")
    return ascmc[0] % 360.0


def _angular_distance(a: float, b: float) -> float:
    diff = abs(a - b) % 360.0
    return min(diff, 360.0 - diff)


def _aspect_delta(natal: float, transiting: float, angle: float) -> float:
    return abs((_angular_distance(natal, transiting)) - angle)


def _month_range(start: date, end: date) -> list[date]:
    dates = []
    current = date(start.year, start.month, 1)
    while current <= end:
        dates.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return dates


def _last_day_of_month(year: int, month: int) -> date:
    if month == 12:
        return date(year + 1, 1, 1) - timedelta(days=1)
    return date(year, month + 1, 1) - timedelta(days=1)


def _date_range(from_ym: str, to_ym: str) -> tuple[date, date]:
    from_year, from_month = map(int, from_ym.split("-"))
    to_year, to_month = map(int, to_ym.split("-"))
    start = date(from_year, from_month, 1)
    end = _last_day_of_month(to_year, to_month)
    return start, end


def _find_event_window(
    *,
    natal_lon: float,
    planet_id: int,
    aspect_angle: float,
    orb: float,
    range_start: date,
    range_end: date,
) -> tuple[date, date, date, float] | None:
    monthly_dates = _month_range(range_start, range_end)
    best_month = None
    best_delta = 999.0
    for month_start in monthly_dates:
        dt = datetime(month_start.year, month_start.month, 1, tzinfo=timezone.utc)
        trans_lon = _planet_longitude(dt, planet_id)
        delta = _aspect_delta(natal_lon, trans_lon, aspect_angle)
        if delta < best_delta:
            best_delta = delta
            best_month = month_start

    if best_month is None:
        return None

    window_start = date(best_month.year, best_month.month, 1) - timedelta(days=31)
    window_end = _last_day_of_month(best_month.year, best_month.month) + timedelta(days=31)
    window_start = max(window_start, range_start)
    window_end = min(window_end, range_end)

    current = window_start
    inside = False
    first_day = None
    last_day = None
    peak_day = None
    peak_delta = 999.0
    while current <= window_end:
        dt = datetime(current.year, current.month, current.day, tzinfo=timezone.utc)
        trans_lon = _planet_longitude(dt, planet_id)
        delta = _aspect_delta(natal_lon, trans_lon, aspect_angle)
        if delta < peak_delta:
            peak_delta = delta
            peak_day = current
        if delta <= orb:
            if not inside:
                first_day = current
                inside = True
            last_day = current
        current += timedelta(days=1)

    if first_day is None or last_day is None or peak_day is None:
        return None

    return first_day, last_day, peak_day, peak_delta


def build_western_transit_cycles(
    *,
    birth: dict[str, Any],
    range_from: str,
    range_to: str,
    as_of: str | None = None,
) -> list[dict[str, Any]]:
    dt_utc = _to_utc(
        birth.get("date", ""),
        birth.get("time", ""),
        birth.get("timezone", "UTC"),
    )
    lat = birth.get("location", {}).get("lat", 0.0)
    lon = birth.get("location", {}).get("lon", 0.0)

    natal = {
        "sun": _planet_longitude(dt_utc, swe.SUN),
        "moon": _planet_longitude(dt_utc, swe.MOON),
        "saturn": _planet_longitude(dt_utc, swe.SATURN),
        "jupiter": _planet_longitude(dt_utc, swe.JUPITER),
        "asc": _ascendant_longitude(dt_utc, lat, lon),
    }

    range_from_norm = normalize_iso_ym(range_from)
    range_to_norm = normalize_iso_ym(range_to)
    range_start, range_end = _date_range(range_from_norm, range_to_norm)

    cycles: list[dict[str, Any]] = []

    for kind, planet_id, natal_key, orb, polarity, intensity in (
        ("return_saturn", swe.SATURN, "saturn", _ORB_RETURN, "challenging", 0.85),
        ("return_jupiter", swe.JUPITER, "jupiter", _ORB_RETURN, "supporting", 0.65),
    ):
        result = _find_event_window(
            natal_lon=natal[natal_key],
            planet_id=planet_id,
            aspect_angle=0.0,
            orb=orb,
            range_start=range_start,
            range_end=range_end,
        )
        if result is None:
            continue
        start_day, end_day, peak_day, delta = result
        trans_lon = _planet_longitude(
            datetime(peak_day.year, peak_day.month, peak_day.day, tzinfo=timezone.utc),
            planet_id,
        )
        start_str = normalize_iso_ym(start_day)
        end_str = normalize_iso_ym(end_day)
        peak_str = peak_day.strftime("%Y-%m-%d")
        cycles.append(
            {
                "cycleId": stable_id(["western", kind, natal_key, start_str, end_str]),
                "system": "western",
                "kind": kind,
                "domain": "growth",
                "themes": _EVENT_THEMES[kind],
                "start": start_str,
                "end": end_str,
                "peak": peak_str,
                "intensity": clamp01(intensity),
                "polarity": polarity,
                "evidence": [
                    {
                        "source": "western.natal.longitude",
                        "value": {"planet": natal_key, "longitude": round(natal[natal_key], 2)},
                        "weight": 0.8,
                        "note": "Natal longitude.",
                    },
                    {
                        "source": "western.transit.peak",
                        "value": {"longitude": round(trans_lon, 2), "delta": round(delta, 2)},
                        "weight": 0.6,
                        "note": "Closest approach within orb.",
                    },
                    {
                        "source": "western.transit.method",
                        "value": "monthly+daily",
                        "weight": 0.4,
                        "note": "Coarse-to-fine scan.",
                    },
                ],
                "notes": [],
            }
        )

    for target_key, domain in (("sun", "career"), ("moon", "relationships"), ("asc", "growth")):
        for aspect_name, angle in _ASPECTS.items():
            result = _find_event_window(
                natal_lon=natal[target_key],
                planet_id=swe.SATURN,
                aspect_angle=angle,
                orb=_ORB_SATURN_ASPECT,
                range_start=range_start,
                range_end=range_end,
            )
            if result is None:
                continue
            start_day, end_day, peak_day, delta = result
            trans_lon = _planet_longitude(
                datetime(peak_day.year, peak_day.month, peak_day.day, tzinfo=timezone.utc),
                swe.SATURN,
            )
            start_str = normalize_iso_ym(start_day)
            end_str = normalize_iso_ym(end_day)
            peak_str = peak_day.strftime("%Y-%m-%d")
            cycles.append(
                {
                    "cycleId": stable_id(
                        ["western", "transit_saturn_aspect", target_key, aspect_name, start_str, end_str]
                    ),
                    "system": "western",
                    "kind": "transit_saturn_aspect",
                    "domain": domain,
                    "themes": _EVENT_THEMES["transit_saturn_aspect"]
                    + [f"aspect:{aspect_name}", f"target:{target_key}"],
                    "start": start_str,
                    "end": end_str,
                    "peak": peak_str,
                    "intensity": clamp01(0.75),
                    "polarity": "challenging",
                    "evidence": [
                        {
                            "source": "western.natal.longitude",
                            "value": {"planet": target_key, "longitude": round(natal[target_key], 2)},
                            "weight": 0.8,
                            "note": "Natal longitude.",
                        },
                        {
                            "source": "western.transit.peak",
                            "value": {"aspect": aspect_name, "longitude": round(trans_lon, 2), "delta": round(delta, 2)},
                            "weight": 0.6,
                            "note": "Closest approach within orb.",
                        },
                        {
                            "source": "western.transit.method",
                            "value": "monthly+daily",
                            "weight": 0.4,
                            "note": "Coarse-to-fine scan.",
                        },
                    ],
                    "notes": [],
                }
            )

    return sort_cycles(cycles)

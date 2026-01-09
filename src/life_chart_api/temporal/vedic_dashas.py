from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

import swisseph as swe

from life_chart_api.temporal.models import clamp01, normalize_iso_ym, sort_cycles, stable_id

_DASHA_SEQUENCE = [
    ("Ketu", 7),
    ("Venus", 20),
    ("Sun", 6),
    ("Moon", 10),
    ("Mars", 7),
    ("Rahu", 18),
    ("Jupiter", 16),
    ("Saturn", 19),
    ("Mercury", 17),
]

_DASHA_TAGS = {
    "Sun": ["visibility", "authority"],
    "Moon": ["emotions", "belonging"],
    "Mars": ["drive", "conflict"],
    "Mercury": ["learning", "trade"],
    "Jupiter": ["growth", "guidance"],
    "Venus": ["relationships", "comfort"],
    "Saturn": ["discipline", "responsibility"],
    "Rahu": ["disruption", "ambition"],
    "Ketu": ["detachment", "spirituality"],
}

_DASHA_POLARITY = {
    "Sun": "neutral",
    "Moon": "neutral",
    "Mars": "neutral",
    "Mercury": "neutral",
    "Jupiter": "supporting",
    "Venus": "supporting",
    "Saturn": "challenging",
    "Rahu": "challenging",
    "Ketu": "challenging",
}

_DASHA_INTENSITY = {
    "Sun": 0.65,
    "Moon": 0.6,
    "Mars": 0.65,
    "Mercury": 0.6,
    "Jupiter": 0.7,
    "Venus": 0.7,
    "Saturn": 0.75,
    "Rahu": 0.75,
    "Ketu": 0.7,
}

_NAKSHATRA_NAMES = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]


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


def _moon_sidereal_longitude(dt_utc: datetime) -> float:
    jd_ut = _julday_ut(dt_utc)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    values, _ = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)
    lon = (values[0] - ayanamsa) % 360.0
    return lon


def _nakshatra_index_and_fraction(lon: float) -> tuple[int, float]:
    segment = 360.0 / 27.0
    index = int(lon // segment)
    offset = lon % segment
    return index, offset / segment


def _lord_for_nakshatra(index: int) -> str:
    return _DASHA_SEQUENCE[index % len(_DASHA_SEQUENCE)][0]


def _add_months(start: date, months: int) -> date:
    year = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    return date(year, month, 1)


def _overlaps(start: str, end: str, range_from: str, range_to: str) -> bool:
    return start <= range_to and end >= range_from


def build_vedic_dasha_cycles(
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
    moon_lon = _moon_sidereal_longitude(dt_utc)
    nak_index, fraction = _nakshatra_index_and_fraction(moon_lon)
    nak_name = _NAKSHATRA_NAMES[nak_index]
    start_lord = _lord_for_nakshatra(nak_index)

    range_from_norm = normalize_iso_ym(range_from)
    range_to_norm = normalize_iso_ym(range_to)

    birth_month_start = date(dt_utc.year, dt_utc.month, 1)

    sequence = [lord for lord, _ in _DASHA_SEQUENCE]
    durations = {lord: years for lord, years in _DASHA_SEQUENCE}

    cycles: list[dict[str, Any]] = []
    current_start = birth_month_start

    start_years_full = durations[start_lord]
    remaining_years = start_years_full * (1.0 - fraction)
    remaining_months = max(1, int(round(remaining_years * 12)))

    sequence_index = sequence.index(start_lord)
    cycle_count = 0
    while len(cycles) < 36 and current_start.strftime("%Y-%m") <= range_to_norm:
        lord = sequence[sequence_index % len(sequence)]
        if cycle_count == 0:
            months = remaining_months
        else:
            months = int(round(durations[lord] * 12))
        end_date = _add_months(current_start, months)
        start_str = current_start.strftime("%Y-%m")
        end_str = end_date.strftime("%Y-%m")

        if _overlaps(start_str, end_str, range_from_norm, range_to_norm):
            cycle = {
                "cycleId": stable_id(["vedic", "maha", lord, start_str, end_str]),
                "system": "vedic",
                "kind": "dasha_maha",
                "domain": "growth",
                "themes": _DASHA_TAGS.get(lord, ["scaffold"]),
                "start": start_str,
                "end": end_str,
                "intensity": clamp01(_DASHA_INTENSITY.get(lord, 0.6)),
                "polarity": _DASHA_POLARITY.get(lord, "neutral"),
                "evidence": [
                    {
                        "source": "vedic.vimshottari.lord",
                        "value": lord,
                        "weight": 0.8,
                        "note": "Mahadasha lord.",
                    },
                    {
                        "source": "vedic.nakshatra",
                        "value": {"index": nak_index + 1, "name": nak_name},
                        "weight": 0.7,
                        "note": "Birth nakshatra.",
                    },
                    {
                        "source": "vedic.vimshottari.sequence",
                        "value": sequence,
                        "weight": 0.5,
                        "note": "Standard Vimshottari order.",
                    },
                ],
                "notes": ["approx: sidereal moon longitude"],
            }
            if cycle_count == 0 and 0.0 < fraction < 1.0:
                cycle["evidence"].append(
                    {
                        "source": "vedic.vimshottari.assumptions",
                        "value": {"fraction_completed": round(fraction, 3)},
                        "weight": 0.2,
                        "note": "Approx: fractional start based on moon longitude.",
                    }
                )
            cycles.append(cycle)

        current_start = end_date
        sequence_index += 1
        cycle_count += 1

    return sort_cycles(cycles)

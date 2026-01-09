from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from life_chart_api.schemas.example_loader import load_example_json, stamp_meta_and_input
from life_chart_api.synthesis.overlay_chinese import (
    compute_chinese_tier1,
    compute_chinese_tier2,
    overlay_chinese_tier1,
    overlay_chinese_tier2,
)
from life_chart_api.inputs.query_parsers import (
    parse_granularity,
    parse_ymd,
    parse_include_csv,
    validate_range,
)
from life_chart_api.temporal.chinese_luck_pillars import build_chinese_luck_pillar_cycles
from life_chart_api.temporal.scaffold import build_timeline_scaffold
from life_chart_api.temporal.temporal_intersection import build_temporal_intersection_cycles
from life_chart_api.temporal.vedic_dashas import build_vedic_dasha_cycles
from life_chart_api.temporal.western_transits import build_western_transit_cycles
from life_chart_api.temporal.models import sort_cycles
from life_chart_api.settings import get_settings

router = APIRouter(prefix="/profile", tags=["profile"])


class TimelineScaffoldRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str | None = None
    date: str
    time: str
    timezone: str
    city: str
    region: str
    country: str
    lat: float
    lon: float
    from_: str = Field("2026-01", alias="from")
    to: str = Field("2027-12")


@router.get("/timeline/scaffold")
def get_timeline_scaffold(
    payload: TimelineScaffoldRequest = Depends(),
    request: Request = None,
) -> dict:
    settings = get_settings()
    raw_from = request.query_params.get("from") if request else None
    raw_to = request.query_params.get("to") if request else None
    range_from, range_to = validate_range(
        range_from=raw_from or payload.from_,
        range_to=raw_to or payload.to,
        granularity="month",
        path_from="query.from",
        path_to="query.to",
        max_months=settings.MAX_TIMELINE_RANGE_MONTHS,
        max_quarters=settings.MAX_RANGE_QUARTERS,
    )
    birth = {
        "date": payload.date,
        "time": payload.time,
        "timezone": payload.timezone,
        "location": {
            "city": payload.city,
            "region": payload.region,
            "country": payload.country,
            "lat": payload.lat,
            "lon": payload.lon,
        },
    }

    return build_timeline_scaffold(
        name=payload.name,
        birth=birth,
        range_from=range_from,
        range_to=range_to,
    )


class TimelineRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    name: str | None = None
    date: str
    time: str
    timezone: str
    city: str
    region: str
    country: str
    lat: float
    lon: float
    from_: str = Field("2026-01", alias="from")
    to: str = Field("2027-12")
    include: str | None = None
    as_of: str | None = None
    granularity: str = "month"


@router.get("/timeline")
def get_timeline(payload: TimelineRequest = Depends(), request: Request = None) -> dict:
    settings = get_settings()
    raw_from = request.query_params.get("from") if request else None
    raw_to = request.query_params.get("to") if request else None
    granularity = parse_granularity(payload.granularity, path="query.granularity")
    range_from, range_to = validate_range(
        range_from=raw_from or payload.from_,
        range_to=raw_to or payload.to,
        granularity=granularity,
        path_from="query.from",
        path_to="query.to",
        max_months=settings.MAX_TIMELINE_RANGE_MONTHS,
        max_quarters=settings.MAX_RANGE_QUARTERS,
    )
    include = parse_include_csv(
        payload.include,
        allowed={"vedic", "chinese", "western", "intersection_time"},
        default="vedic",
        path="query.include",
    )
    as_of = parse_ymd(payload.as_of, path="query.as_of") if payload.as_of else None
    birth = {
        "date": payload.date,
        "time": payload.time,
        "timezone": payload.timezone,
        "location": {
            "city": payload.city,
            "region": payload.region,
            "country": payload.country,
            "lat": payload.lat,
            "lon": payload.lon,
        },
    }

    cycles: list[dict] = []

    if "vedic" in include:
        cycles.extend(
            build_vedic_dasha_cycles(
                birth=birth,
                range_from=range_from,
                range_to=range_to,
                as_of=as_of,
            )
        )

    if "chinese" in include:
        chinese = stamp_meta_and_input(
            load_example_json("chinese_profile.example.json"),
            payload.name or "Unknown",
            birth,
        )
        tier1 = compute_chinese_tier1(
            date_str=birth.get("date", ""),
            time_str=birth.get("time", ""),
            tz=birth.get("timezone", ""),
        )
        chinese = overlay_chinese_tier1(chinese, tier1)
        tier2 = compute_chinese_tier2(
            date_str=birth.get("date", ""),
            time_str=birth.get("time", ""),
            tz=birth.get("timezone", ""),
            tier1=tier1,
        )
        chinese = overlay_chinese_tier2(chinese, tier2)
        cycles.extend(
            build_chinese_luck_pillar_cycles(
                chinese_system_output=chinese,
                range_from=range_from,
                range_to=range_to,
                as_of=as_of,
            )
        )

    if "western" in include:
        cycles.extend(
            build_western_transit_cycles(
                birth=birth,
                range_from=range_from,
                range_to=range_to,
                as_of=as_of,
            )
        )

    if "intersection_time" in include:
        cycles.extend(
            build_temporal_intersection_cycles(
                cycles,
                range_from,
                range_to,
                granularity,
            )
        )

    cycles = sort_cycles(cycles)

    response = {
        "meta": {"version": "phase2.3"},
        "input": {"birth": birth},
        "range": {"from": range_from, "to": range_to},
        "cycles": cycles,
    }
    if payload.name:
        response["input"]["name"] = payload.name
    return response

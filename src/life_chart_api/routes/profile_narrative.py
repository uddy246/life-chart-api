from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from life_chart_api.engines.intersection_engine import build_intersection_report, extract_signals
from life_chart_api.inputs.query_parsers import parse_granularity, parse_include_csv, parse_tone, parse_ymd
from life_chart_api.narrative.narrative_view import build_narrative_response
from life_chart_api.routes.profile_forecast import build_forecast_from_payload
from life_chart_api.routes.profile_compute import ProfileComputeRequest, compute_profile

router = APIRouter(prefix="/profile", tags=["profile"])


def _normalize_country(country: str | None) -> str:
    if not country:
        return ""
    normalized = country.strip()
    lower = normalized.lower()
    if lower in {"uk", "u.k.", "united kingdom", "great britain", "britain", "gb"}:
        return "UK"
    return normalized


def _should_use_default_london(
    *,
    city: str | None,
    region: str | None,
    country: str | None,
    lat: str | None,
    lon: str | None,
) -> bool:
    if lat is not None or lon is not None:
        return False
    if (city or "").strip().lower() != "london":
        return False
    if (region or "").strip().lower() != "england":
        return False
    if (country or "").strip().lower() not in {"uk", "u.k.", "united kingdom", "great britain", "britain", "gb"}:
        return False
    return True

class NarrativeRequest(BaseModel):
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
    granularity: str = "month"
    as_of: str | None = None
    tone: str = "neutral"


def _apply_query_overrides(
    payload: NarrativeRequest,
    request: Request | None,
) -> tuple[NarrativeRequest, str | None, str | None]:
    if not request:
        return payload, None, None

    params = request.query_params
    updates: dict[str, str] = {}
    if "include" in params:
        updates["include"] = params.get("include", "")
    if "granularity" in params:
        updates["granularity"] = params.get("granularity", "")
    if "tone" in params:
        updates["tone"] = params.get("tone", "")

    if updates:
        payload = payload.model_copy(update=updates)

    return payload, params.get("from"), params.get("to")


@router.get("/narrative")
def get_narrative(request: Request) -> dict:
    params = request.query_params
    use_query_prefix = any(key.startswith("query.") for key in params.keys())
    if use_query_prefix:
        name = params.get("query.name")
        dob = params.get("query.dob")
        time = params.get("query.tob") or params.get("query.time") or "12:00"
        timezone = params.get("query.timezone") or "Europe/London"
        city = params.get("query.city") or "London"
        region = params.get("query.region") or "England"
        country = _normalize_country(params.get("query.country") or "UK")
        lat = params.get("query.lat")
        lon = params.get("query.lon")
        if _should_use_default_london(city=city, region=region, country=country, lat=lat, lon=lon):
            lat = "51.5074"
            lon = "-0.1278"
        missing_fields = []
        if not name:
            missing_fields.append("name")
        if not dob:
            missing_fields.append("dob")
        if missing_fields:
            detail = [
                {"loc": ["query", field], "msg": "Field required", "type": "value_error.missing"}
                for field in missing_fields
            ]
            return JSONResponse(status_code=422, content={"detail": detail})
    else:
        name = params.get("name")
        dob = params.get("dob")
        time = params.get("tob") or params.get("time") or params.get("h") or "12:00"
        timezone = params.get("timezone") or "Europe/London"
        city = params.get("city") or "London"
        region = params.get("region") or "England"
        country = _normalize_country(params.get("country") or "UK")
        lat = params.get("lat")
        lon = params.get("lon")
        if _should_use_default_london(city=city, region=region, country=country, lat=lat, lon=lon):
            lat = "51.5074"
            lon = "-0.1278"
        missing_fields = []
        if not name:
            missing_fields.append("name")
        if not dob:
            missing_fields.append("dob")
        if missing_fields:
            detail = [
                {"loc": ["query", field], "msg": "Field required", "type": "value_error.missing"}
                for field in missing_fields
            ]
            return JSONResponse(status_code=422, content={"detail": detail})

    date = parse_ymd(dob, path="query.dob")
    include_list = parse_include_csv(
        params.get("include"),
        allowed={"western", "vedic", "chinese"},
        default="western,vedic,chinese",
        path="query.include",
    )
    granularity_value = parse_granularity(params.get("granularity"), path="query.granularity")

    birth = {
        "date": date,
        "time": time,
        "timezone": timezone,
        # TODO: replace default location once Lovable sends location fields.
        "location": {
            "city": city,
            "region": region,
            "country": country,
            "lat": float(lat) if lat is not None else None,
            "lon": float(lon) if lon is not None else None,
        },
    }

    payload = ProfileComputeRequest.model_validate({"name": name or "Unknown", "birth": birth})
    profile = compute_profile(payload)
    intersection = build_intersection_report(extract_signals(profile))
    return {
        "profile": profile,
        "intersection": intersection.model_dump(),
        "narrative": {
            "granularity": granularity_value,
            "include": include_list,
            "note": "compat response",
        },
    }


@router.post("/narrative")
def post_narrative(payload: NarrativeRequest, request: Request = None) -> dict:
    payload, raw_from, raw_to = _apply_query_overrides(payload, request)
    forecast = build_forecast_from_payload(payload, raw_from=raw_from, raw_to=raw_to)
    tone = parse_tone(payload.tone, path="query.tone")
    return build_narrative_response(forecast, tone=tone)

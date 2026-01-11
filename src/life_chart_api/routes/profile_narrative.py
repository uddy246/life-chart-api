from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from life_chart_api.inputs.query_parsers import parse_tone, parse_ymd
from life_chart_api.narrative.narrative_view import build_narrative_response
from life_chart_api.routes.profile_compute import _try_geocode_location
from life_chart_api.routes.profile_forecast import build_forecast_from_payload
from life_chart_api.schemas.profile_response_builder import build_profile_response

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


def _build_birth(payload: NarrativeRequest) -> dict[str, Any]:
    return {
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


def _build_narrative_envelope(
    payload: NarrativeRequest,
    forecast: dict[str, Any],
    tone: str,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    birth = _build_birth(payload)
    profile = build_profile_response(name=payload.name or "Unknown", birth=birth, numerology=None)
    if warnings:
        profile["warnings"] = warnings
    narrative = build_narrative_response(forecast, tone=tone)
    return {"profile": profile, "intersection": profile.get("intersection", {}), "narrative": narrative}


def _get_query_param(params, key: str, use_query_prefix: bool) -> str | None:
    return params.get(f"query.{key}") if use_query_prefix else params.get(key)


@router.get("/narrative")
def get_narrative(request: Request) -> dict:
    params = request.query_params
    use_query_prefix = any(key.startswith("query.") for key in params.keys())
    if use_query_prefix:
        name = _get_query_param(params, "name", use_query_prefix)
        dob = (
            _get_query_param(params, "dob", use_query_prefix)
            or _get_query_param(params, "date", use_query_prefix)
            or _get_query_param(params, "dateOfBirth", use_query_prefix)
        )
        time = (
            _get_query_param(params, "tob", use_query_prefix)
            or _get_query_param(params, "time", use_query_prefix)
            or "12:00"
        )
        timezone = _get_query_param(params, "timezone", use_query_prefix) or "Europe/London"
        city = _get_query_param(params, "city", use_query_prefix) or "London"
        region = _get_query_param(params, "region", use_query_prefix) or "England"
        country = _normalize_country(_get_query_param(params, "country", use_query_prefix) or "UK")
        lat = _get_query_param(params, "lat", use_query_prefix)
        lon = _get_query_param(params, "lon", use_query_prefix)
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
        name = _get_query_param(params, "name", use_query_prefix)
        dob = (
            _get_query_param(params, "dob", use_query_prefix)
            or _get_query_param(params, "date", use_query_prefix)
            or _get_query_param(params, "dateOfBirth", use_query_prefix)
        )
        time = (
            _get_query_param(params, "tob", use_query_prefix)
            or _get_query_param(params, "time", use_query_prefix)
            or _get_query_param(params, "h", use_query_prefix)
            or "12:00"
        )
        timezone = _get_query_param(params, "timezone", use_query_prefix) or "Europe/London"
        city = _get_query_param(params, "city", use_query_prefix) or "London"
        region = _get_query_param(params, "region", use_query_prefix) or "England"
        country = _normalize_country(_get_query_param(params, "country", use_query_prefix) or "UK")
        lat = _get_query_param(params, "lat", use_query_prefix)
        lon = _get_query_param(params, "lon", use_query_prefix)
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

    warnings: list[str] = []
    if lat is None or lon is None:
        if _should_use_default_london(city=city, region=region, country=country, lat=lat, lon=lon):
            lat = "51.5074"
            lon = "-0.1278"
        else:
            resolved_lat, resolved_lon, geocode_failed = _try_geocode_location(city, region, country)
            if geocode_failed:
                warnings.append("geocoding_unavailable")
                resolved_lat, resolved_lon = 0.0, 0.0
            lat = resolved_lat
            lon = resolved_lon

    date = parse_ymd(dob, path="query.dob")
    include = _get_query_param(params, "include", use_query_prefix)
    granularity = _get_query_param(params, "granularity", use_query_prefix)
    tone_value = _get_query_param(params, "tone", use_query_prefix)
    raw_from = _get_query_param(params, "from", use_query_prefix)
    raw_to = _get_query_param(params, "to", use_query_prefix)
    as_of = _get_query_param(params, "as_of", use_query_prefix)

    payload = NarrativeRequest.model_validate(
        {
            "name": name or "Unknown",
            "date": date,
            "time": time,
            "timezone": timezone,
            "city": city,
            "region": region,
            "country": country,
            "lat": float(lat) if lat is not None else 0.0,
            "lon": float(lon) if lon is not None else 0.0,
            "include": include,
            "granularity": granularity or "month",
            "tone": tone_value or "neutral",
            "as_of": as_of,
        }
    )
    forecast = build_forecast_from_payload(payload, raw_from=raw_from, raw_to=raw_to)
    tone = parse_tone(payload.tone, path="query.tone")
    return _build_narrative_envelope(payload, forecast, tone, warnings)


@router.post("/narrative")
def post_narrative(payload: NarrativeRequest, request: Request = None) -> dict:
    payload, raw_from, raw_to = _apply_query_overrides(payload, request)
    forecast = build_forecast_from_payload(payload, raw_from=raw_from, raw_to=raw_to)
    tone = parse_tone(payload.tone, path="query.tone")
    return _build_narrative_envelope(payload, forecast, tone)

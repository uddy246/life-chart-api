from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field

from life_chart_api.convergent.profile_compute import compute_convergent_profile
from life_chart_api.convergent.window_enrichment import enrich_windows_with_identity
from life_chart_api.inputs.query_parsers import parse_tone, parse_ymd
from life_chart_api.narrative.deep_reading import synthesize_deep_reading
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


_FALLBACK_HEADLINE = "Narrative unavailable."


def _fallback_summary(range_from: str, range_to: str) -> list[str]:
    return [
        "Narrative unavailable for the selected range.",
        f"Range covers {range_from} to {range_to}.",
        "No high-confidence windows available.",
    ]


def _build_minimal_fallback_narrative(
    payload: NarrativeRequest,
    tone: str,
    *,
    range_from: str,
    range_to: str,
    granularity: str,
    as_of: str | None,
    summary: list[str],
) -> dict[str, Any]:
    birth = _build_birth(payload)
    overview = {
        "headline": _FALLBACK_HEADLINE,
        "bullets": summary[:6],
        "citations": [],
    }
    domain_bullets = summary[:2]
    by_domain = {}
    for domain in ("career", "relationships", "growth"):
        by_domain[domain] = {
            "headline": f"No strong {domain} windows in this range.",
            "bullets": domain_bullets,
            "topWindows": [],
        }
    response = {
        "meta": {
            "version": "phase3.2",
            "granularity": granularity,
            "range": {"from": range_from, "to": range_to},
        },
        "input": {"name": payload.name or "Unknown", "birth": birth},
        "overview": overview,
        "windows": [],
        "byDomain": by_domain,
        "style": {"tone": tone, "readingLevel": "plain"},
    }
    if as_of:
        response["meta"]["as_of"] = as_of
    return response


def _build_fallback_narrative(
    payload: NarrativeRequest,
    tone: str,
    forecast: dict[str, Any] | None,
) -> dict[str, Any]:
    birth = _build_birth(payload)
    meta = forecast.get("meta") if isinstance(forecast, dict) else {}
    meta_range = meta.get("range") if isinstance(meta, dict) else {}
    range_from = meta_range.get("from") if isinstance(meta_range, dict) else None
    range_to = meta_range.get("to") if isinstance(meta_range, dict) else None
    granularity = meta.get("granularity") if isinstance(meta, dict) else None
    as_of = meta.get("as_of") if isinstance(meta, dict) else None
    summary = forecast.get("summary") if isinstance(forecast, dict) else None
    if not isinstance(summary, list) or len(summary) < 3:
        summary = _fallback_summary(range_from or payload.from_, range_to or payload.to)

    forecast_stub = {
        "meta": {
            "version": "phase2.4",
            "granularity": granularity or payload.granularity or "month",
            "range": {
                "from": range_from or payload.from_,
                "to": range_to or payload.to,
            },
        },
        "input": {"name": payload.name or "Unknown", "birth": birth},
        "topWindows": [],
        "summary": summary,
    }
    if as_of:
        forecast_stub["meta"]["as_of"] = as_of
    try:
        response = build_narrative_response(forecast_stub, tone=tone)
    except Exception:
        return _build_minimal_fallback_narrative(
            payload,
            tone,
            range_from=forecast_stub["meta"]["range"]["from"],
            range_to=forecast_stub["meta"]["range"]["to"],
            granularity=forecast_stub["meta"]["granularity"],
            as_of=as_of,
            summary=summary,
        )
    overview = response.get("overview")
    if isinstance(overview, dict):
        overview["headline"] = _FALLBACK_HEADLINE
        bullets = overview.get("bullets")
        if not isinstance(bullets, list) or len(bullets) < 3:
            overview["bullets"] = _fallback_summary(
                forecast_stub["meta"]["range"]["from"],
                forecast_stub["meta"]["range"]["to"],
            )
        citations = overview.get("citations")
        if not isinstance(citations, list):
            overview["citations"] = []
    return response


def _summarize_overview(overview_value: Any) -> tuple[str, dict[str, Any] | None]:
    if isinstance(overview_value, dict):
        bullets = overview_value.get("bullets")
        if isinstance(bullets, list):
            bullet_texts = [item for item in bullets if isinstance(item, str)]
            if bullet_texts:
                return " ".join(bullet_texts[:3]), overview_value
        text_value = overview_value.get("text")
        if isinstance(text_value, str):
            return text_value, overview_value
        return "", overview_value
    if isinstance(overview_value, list):
        bullet_texts = [item for item in overview_value if isinstance(item, str)]
        if bullet_texts:
            return " ".join(bullet_texts[:3]), None
        return "", None
    if isinstance(overview_value, str):
        return overview_value, None
    return "", None


def _extract_compat_fields(narrative: dict[str, Any]) -> tuple[str, str, list, dict[str, Any] | None]:
    overview_value = narrative.get("overview")
    overview_text, overview_data = _summarize_overview(overview_value)
    headline = ""
    if isinstance(overview_value, dict):
        overview_headline = overview_value.get("headline")
        if isinstance(overview_headline, str):
            headline = overview_headline
    elif isinstance(overview_value, str):
        headline = overview_value
    if not headline:
        narrative_headline = narrative.get("headline")
        if isinstance(narrative_headline, str):
            headline = narrative_headline
    if not isinstance(headline, str):
        headline = ""

    windows = narrative.get("windows")
    if not isinstance(windows, list):
        windows = []

    return overview_text, headline, windows, overview_data


def _build_narrative_envelope(
    payload: NarrativeRequest,
    forecast: dict[str, Any],
    tone: str,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    warnings = list(warnings or [])
    birth = _build_birth(payload)
    profile = build_profile_response(name=payload.name or "Unknown", birth=birth, numerology=None)
    try:
        narrative = build_narrative_response(forecast, tone=tone)
    except Exception:
        if "narrative_unavailable" not in warnings:
            warnings.append("narrative_unavailable")
        narrative = _build_fallback_narrative(payload, tone, forecast)
    if not isinstance(narrative, dict):
        if "narrative_unavailable" not in warnings:
            warnings.append("narrative_unavailable")
        narrative = _build_fallback_narrative(payload, tone, forecast)
    if warnings:
        profile["warnings"] = warnings

    systems = profile.get("systems")
    if isinstance(systems, dict):
        convergent_profile_doc = compute_convergent_profile(
            western=systems.get("western") if isinstance(systems.get("western"), dict) else None,
            vedic=systems.get("vedic") if isinstance(systems.get("vedic"), dict) else None,
            chinese=systems.get("chinese") if isinstance(systems.get("chinese"), dict) else None,
            numerology=systems.get("numerology") if isinstance(systems.get("numerology"), dict) else None,
        )
    else:
        convergent_profile_doc = compute_convergent_profile(None, None, None, None)

    if isinstance(narrative, dict):
        narrative_windows = narrative.get("windows")
        enriched_windows: list[dict] | None = None
        if isinstance(narrative_windows, list):
            enriched_windows = enrich_windows_with_identity(
                narrative_windows,
                convergent_profile_doc,
            )
            narrative["windows"] = enriched_windows
        deep_reading = synthesize_deep_reading(
            convergent_profile_doc,
            enriched_windows or [],
            tone=tone,
            enable_llm=False,
        )
        narrative["deepReading"] = deep_reading

    overview, headline, windows, overview_data = _extract_compat_fields(narrative)

    intersection = profile.get("intersection", {})
    if not isinstance(intersection, dict):
        intersection = {}
    else:
        intersection = dict(intersection)
    intersection["overview"] = overview
    intersection["headline"] = headline
    intersection["windows"] = windows
    if overview_data is not None:
        intersection["overviewData"] = overview_data
    profile["intersection"] = intersection

    response = {
        "profile": profile,
        "intersection": intersection,
        "narrative": narrative,
        "overview": overview,
        "headline": headline,
        "windows": windows,
    }
    if overview_data is not None:
        response["overviewData"] = overview_data
    return response



def _get_query_param(params, key: str, use_query_prefix: bool) -> str | None:
    return params.get(f"query.{key}") if use_query_prefix else params.get(key)


@router.get("/narrative")
def get_narrative(request: Request) -> dict:
    params = request.query_params
    use_query_prefix = any(key.startswith("query.") for key in params.keys())
    warnings: list[str] = []
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
            warnings.extend(f"missing_{field}" for field in missing_fields)
        if not name:
            name = "Unknown"
        if not dob:
            dob = "2000-01-01"
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
            warnings.extend(f"missing_{field}" for field in missing_fields)
        if not name:
            name = "Unknown"
        if not dob:
            dob = "2000-01-01"
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

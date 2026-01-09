from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from life_chart_api.inputs.query_parsers import parse_tone
from life_chart_api.narrative.narrative_view import build_narrative_response
from life_chart_api.routes.profile_forecast import build_forecast_from_payload

router = APIRouter(prefix="/profile", tags=["profile"])


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


@router.get("/narrative")
def get_narrative(payload: NarrativeRequest = Depends(), request: Request = None) -> dict:
    raw_from = request.query_params.get("from") if request else None
    raw_to = request.query_params.get("to") if request else None
    forecast = build_forecast_from_payload(payload, raw_from=raw_from, raw_to=raw_to)
    tone = parse_tone(payload.tone, path="query.tone")
    return build_narrative_response(forecast, tone=tone)

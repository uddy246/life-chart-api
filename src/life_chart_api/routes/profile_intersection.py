from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from life_chart_api.engines.intersection_engine import (
    IntersectionReport,
    build_intersection_report,
    extract_signals,
)

router = APIRouter(prefix="/profile", tags=["profile"])


class IntersectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: dict[str, Any]


@router.post("/intersection", response_model=IntersectionReport)
def compute_intersection(payload: IntersectionRequest) -> IntersectionReport:
    signals = extract_signals(payload.profile)
    return build_intersection_report(signals)

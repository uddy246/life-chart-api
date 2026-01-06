from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class VedicChartFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lagna_sign: str
    lagna_lord: str | None
    moon_sign: str | None
    moon_afflicted: bool = False
    saturn_theme: str | None
    rahu_ketu_emphasis: bool = False
    life_direction_hint: str | None
    timing_sensitivity_hint: str | None
    current_phase_hint: str | None
    notes: List[str] = Field(default_factory=list)

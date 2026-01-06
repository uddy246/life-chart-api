from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class WesternChartFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sun_sign: str
    moon_sign: str
    ascendant_sign: str
    dominant_element: str | None
    dominant_modality: str | None
    mercury_style: str | None
    mars_style: str | None
    venus_style: str | None
    saturn_theme: str | None
    notes: List[str] = Field(default_factory=list)

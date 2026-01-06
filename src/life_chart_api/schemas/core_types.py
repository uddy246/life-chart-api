from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SystemId = Literal["western", "vedic", "chinese", "numerology"]

EmotionalProcessingStyle = Literal[
    "internalised",
    "externalised",
    "cyclical",
    "suppressed",
    "expressive",
]
DecisionStyle = Literal["analytical", "intuitive", "reactive", "strategic", "deliberate"]
TimingSensitivity = Literal[
    "highly_time_sensitive",
    "moderately_cyclical",
    "relatively_stable",
]
DominantPolarity = Literal["yin", "yang", "balanced"]


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceField(StrictBaseModel):
    system: SystemId
    field: str


class DisclaimerBlock(StrictBaseModel):
    id: str
    title: str
    body: str


class SystemUsed(StrictBaseModel):
    system: SystemId
    version: str
    enabled: bool


class BirthPlace(StrictBaseModel):
    name: str
    lat: float
    lon: float
    tz: str


class BirthData(StrictBaseModel):
    date: str
    time: str
    place: BirthPlace


class Subject(StrictBaseModel):
    full_name: str
    birth: BirthData


class QualityCompleteness(StrictBaseModel):
    western: float
    vedic: float
    synthesis: float
    narrative: float


class Quality(StrictBaseModel):
    completeness: QualityCompleteness
    warnings: List[str] = Field(default_factory=list)


class UtcTimestamp(StrictBaseModel):
    value: datetime

    @field_validator("value")
    @classmethod
    def _require_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None or v.tzinfo.utcoffset(v) is None:
            raise ValueError("generated_at_utc must be timezone-aware UTC")
        if v.tzinfo != timezone.utc and v.astimezone(timezone.utc).tzinfo != timezone.utc:
            raise ValueError("generated_at_utc must be UTC")
        return v

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, model_validator

from life_chart_api.schemas.profile_response_builder import build_profile_response

router = APIRouter(prefix="/profile", tags=["profile"])


class BirthLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str
    region: str
    country: str
    lat: float
    lon: float


class BirthInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str
    time: str
    timezone: str
    location: BirthLocation


class ProfileComputeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    birth: BirthInput | None = None
    full_name: str | None = None
    date: str | None = None
    time: str | None = None
    place_name: str | None = None
    lat: float | None = None
    lon: float | None = None
    tz: str | None = None

    @model_validator(mode="after")
    def _validate_shape(self) -> "ProfileComputeRequest":
        if self.name and self.birth:
            return self
        if (
            self.full_name
            and self.date
            and self.time
            and self.place_name
            and self.lat is not None
            and self.lon is not None
            and self.tz
        ):
            return self
        raise ValueError("payload must include name/birth or full_name/date/time/place_name/lat/lon/tz")


@router.post("/compute")
def compute_profile(payload: ProfileComputeRequest) -> dict[str, Any]:
    if payload.name and payload.birth:
        name = payload.name
        birth = payload.birth.model_dump()
    else:
        name = payload.full_name or "Unknown"
        birth = {
            "date": payload.date,
            "time": payload.time,
            "timezone": payload.tz,
            "location": {
                "city": payload.place_name,
                "region": "",
                "country": "",
                "lat": payload.lat,
                "lon": payload.lon,
            },
        }

    return build_profile_response(name=name, birth=birth, numerology=None)

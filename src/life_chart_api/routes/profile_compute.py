from __future__ import annotations

from typing import Any
import os

import requests
from fastapi import APIRouter, HTTPException
from requests import RequestException
from pydantic import BaseModel, ConfigDict, model_validator

from life_chart_api.schemas.profile_response_builder import build_profile_response

router = APIRouter(prefix="/profile", tags=["profile"])
_GEOCODE_CACHE: dict[str, tuple[float, float]] = {}
_GEOCODE_USER_AGENT = "life-chart-api/1.0 (maintainer: life-chart-api team; contact: support@example.com)"
_GEOCODE_HEADERS = {
    "User-Agent": _GEOCODE_USER_AGENT,
    "Accept": "application/json",
    "Accept-Language": "en",
}
_GEOCODE_403_FALLBACKS: dict[str, tuple[float, float]] = {
    "london|england|uk": (51.5074, -0.1278),
    "hyderabad|telangana|india": (17.3850, 78.4867),
}


def _cache_key(city: str, region: str | None, country: str) -> str:
    return "|".join([city.strip().lower(), (region or "").strip().lower(), country.strip().lower()])


def geocode_location(city: str, region: str | None, country: str) -> tuple[float, float]:
    cache_key = _cache_key(city, region, country)
    cached = _GEOCODE_CACHE.get(cache_key)
    if cached:
        return cached

    query_parts = [city]
    if region:
        query_parts.append(region)
    if country:
        query_parts.append(country)
    query = ", ".join(part for part in query_parts if part)

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1},
            headers=_GEOCODE_HEADERS,
            timeout=10,
        )
        if response.status_code == 403:
            allow_fallback = os.getenv("ALLOW_FALLBACK_GEOCODE", "").strip().lower()
            if allow_fallback in {"1", "true", "yes"}:
                fallback = _GEOCODE_403_FALLBACKS.get(cache_key)
                if fallback:
                    _GEOCODE_CACHE[cache_key] = fallback
                    return fallback
            raise HTTPException(
                status_code=502,
                detail="Geocoding provider blocked the request (HTTP 403).",
            )
        response.raise_for_status()
        data = response.json()
    except RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Geocoding request failed: {exc}") from exc

    if not data:
        raise HTTPException(status_code=422, detail=f"Location not found for '{query}'")

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    _GEOCODE_CACHE[cache_key] = (lat, lon)
    return lat, lon


class BirthLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city: str
    region: str | None = None
    country: str
    lat: float | None = None
    lon: float | None = None


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
            and self.tz
        ):
            return self
        raise ValueError("payload must include name/birth or full_name/date/time/place_name/tz")


@router.post("/compute")
def compute_profile(payload: ProfileComputeRequest) -> dict[str, Any]:
    if payload.name and payload.birth:
        name = payload.name
        birth = payload.birth.model_dump()
        location = birth["location"]
        if not location.get("region"):
            location["region"] = ""
        if location.get("lat") is None or location.get("lon") is None:
            lat, lon = geocode_location(location["city"], location.get("region"), location["country"])
            location["lat"] = lat
            location["lon"] = lon
    else:
        name = payload.full_name or "Unknown"
        if payload.lat is None or payload.lon is None:
            lat, lon = geocode_location(payload.place_name or "", None, "")
        else:
            lat, lon = payload.lat, payload.lon
        birth = {
            "date": payload.date,
            "time": payload.time,
            "timezone": payload.tz,
            "location": {
                "city": payload.place_name,
                "region": "",
                "country": "",
                "lat": lat,
                "lon": lon,
            },
        }

    return build_profile_response(name=name, birth=birth, numerology=None)

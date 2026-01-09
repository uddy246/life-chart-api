from __future__ import annotations

from typing import Any

from life_chart_api.astrology.western.compute import compute_western_features
from life_chart_api.schemas.example_loader import load_example_json, stamp_meta_and_input
from life_chart_api.synthesis.overlay_western import overlay_western_tier1
from life_chart_api.synthesis.intersection_engine import build_intersection


def build_profile_response(
    name: str, birth: dict[str, Any], numerology: dict[str, Any] | None = None
) -> dict[str, Any]:
    western = stamp_meta_and_input(load_example_json("western_profile.example.json"), name, birth)
    vedic = stamp_meta_and_input(load_example_json("vedic_profile.example.json"), name, birth)
    chinese = stamp_meta_and_input(load_example_json("chinese_profile.example.json"), name, birth)

    try:
        location = birth.get("location", {})
        computed = compute_western_features(
            date=birth.get("date", ""),
            time=birth.get("time", ""),
            tz=birth.get("timezone", ""),
            lat=location.get("lat", 0.0),
            lon=location.get("lon", 0.0),
        )
        western = overlay_western_tier1(western, computed)
    except Exception:
        pass

    response = {
        "meta": western.get("meta", {}),
        "input": western.get("input", {}),
        "systems": {
            "western": western,
            "vedic": vedic,
            "chinese": chinese,
            "numerology": numerology
            if numerology is not None
            else {"note": "Numerology schema not locked yet; placeholder allowed."},
        },
        "intersection": {},
    }

    response["intersection"] = build_intersection(response)
    return response

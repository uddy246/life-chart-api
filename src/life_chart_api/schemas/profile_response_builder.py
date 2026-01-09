from __future__ import annotations

from typing import Any

from life_chart_api.astrology.western.compute import compute_western_features
from life_chart_api.astrology.vedic.compute import compute_vedic_features
from life_chart_api.numerology.adapter import build_numerology_response_v1
from life_chart_api.schemas.example_loader import load_example_json, stamp_meta_and_input
from life_chart_api.synthesis.overlay_chinese import (
    compute_chinese_tier1,
    compute_chinese_tier2,
    overlay_chinese_tier1,
    overlay_chinese_tier2,
)
from life_chart_api.synthesis.overlay_vedic import overlay_vedic_tier1, overlay_vedic_tier2
from life_chart_api.synthesis.overlay_western import overlay_western_tier1, overlay_western_tier2
from life_chart_api.synthesis.intersection_engine import build_intersection
from life_chart_api.synthesis.intersection_engine_v2 import build_intersection_v2


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
        western = overlay_western_tier2(western, computed)
    except Exception:
        pass

    try:
        location = birth.get("location", {})
        computed = compute_vedic_features(
            date=birth.get("date", ""),
            time=birth.get("time", ""),
            tz=birth.get("timezone", ""),
            lat=location.get("lat", 0.0),
            lon=location.get("lon", 0.0),
        )
        vedic = overlay_vedic_tier1(vedic, computed)
        vedic = overlay_vedic_tier2(vedic, computed)
    except Exception:
        pass

    try:
        tier1 = compute_chinese_tier1(
            date_str=birth.get("date", ""),
            time_str=birth.get("time", ""),
            tz=birth.get("timezone", ""),
        )
        chinese = overlay_chinese_tier1(chinese, tier1)
        tier2 = compute_chinese_tier2(
            date_str=birth.get("date", ""),
            time_str=birth.get("time", ""),
            tz=birth.get("timezone", ""),
            tier1=tier1,
        )
        chinese = overlay_chinese_tier2(chinese, tier2)
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
            else build_numerology_response_v1(
                full_name_birth=name,
                dob=birth.get("date", ""),
                forecast_year=None,
                as_of_date=None,
            ).model_dump(),
        },
        "intersection": {},
    }

    response["intersection"] = build_intersection(response)
    response["intersection"]["v2"] = build_intersection_v2(response)
    return response

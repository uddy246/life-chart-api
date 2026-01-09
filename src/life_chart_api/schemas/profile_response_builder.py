from __future__ import annotations

from typing import Any

from life_chart_api.schemas.example_loader import load_example_json, stamp_meta_and_input
from life_chart_api.synthesis.intersection_engine import build_intersection


def build_profile_response(
    name: str, birth: dict[str, Any], numerology: dict[str, Any] | None = None
) -> dict[str, Any]:
    western = stamp_meta_and_input(load_example_json("western_profile.example.json"), name, birth)
    vedic = stamp_meta_and_input(load_example_json("vedic_profile.example.json"), name, birth)
    chinese = stamp_meta_and_input(load_example_json("chinese_profile.example.json"), name, birth)

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

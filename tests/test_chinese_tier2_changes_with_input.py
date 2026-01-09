import json
from pathlib import Path

import jsonschema
try:
    from fastapi.testclient import TestClient
    _HAS_TESTCLIENT = True
except RuntimeError:
    TestClient = None
    _HAS_TESTCLIENT = False
from referencing import Registry, Resource

from life_chart_api.main import app
from life_chart_api.routes.profile_compute import ProfileComputeRequest, compute_profile


def _registry_for_schema(schema_path: Path) -> Registry:
    schema_dir = schema_path.parent
    western_path = schema_dir / "western_profile.schema.json"
    vedic_path = schema_dir / "vedic_profile.schema.json"
    chinese_path = schema_dir / "chinese_profile.schema.json"

    def load_resource(path: Path, contents: dict | None = None):
        uri = path.resolve().as_uri()
        if contents is None:
            contents = json.loads(path.read_text(encoding="utf-8"))
        return uri, Resource.from_contents(contents)

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_with_id = dict(schema)
    schema_with_id["$id"] = schema_path.resolve().as_uri()

    return Registry().with_resources(
        [
            load_resource(schema_path, schema_with_id),
            load_resource(western_path),
            load_resource(vedic_path),
            load_resource(chinese_path),
        ]
    )


def _extract_chinese_tier2(chinese: dict) -> dict[str, object]:
    day_master = chinese.get("dayMaster", {})
    elements = chinese.get("elements", {})
    ten_gods = chinese.get("tenGods", {})
    return {
        "strength": day_master.get("strength") if isinstance(day_master, dict) else None,
        "favourable": elements.get("favourable") if isinstance(elements, dict) else None,
        "dominant": ten_gods.get("dominant") if isinstance(ten_gods, dict) else None,
    }


def _request_payload(date: str) -> dict:
    return {
        "name": "Example Person",
        "birth": {
            "date": date,
            "time": "14:00:00",
            "timezone": "UTC",
            "location": {
                "city": "Hyderabad",
                "region": "Telangana",
                "country": "India",
                "lat": 17.385,
                "lon": 78.4867,
            },
        },
    }


def _post_profile(payload: dict) -> dict:
    if _HAS_TESTCLIENT:
        client = TestClient(app)
        response = client.post("/profile/compute", json=payload)
        assert response.status_code == 200
        return response.json()
    model = ProfileComputeRequest.model_validate(payload)
    return compute_profile(model)


def test_chinese_tier2_changes_with_input():
    payload_a = _request_payload("1999-02-26")
    payload_b = _request_payload("1999-07-26")

    response_a = _post_profile(payload_a)
    response_b = _post_profile(payload_b)

    schema_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "life_chart_api"
        / "schemas"
        / "profile_response.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_with_id = dict(schema)
    schema_with_id["$id"] = schema_path.resolve().as_uri()

    registry = _registry_for_schema(schema_path)
    validator_cls = jsonschema.validators.validator_for(schema_with_id)
    validator = validator_cls(schema_with_id, registry=registry)
    validator.validate(response_a)
    validator.validate(response_b)

    chinese_a = response_a.get("systems", {}).get("chinese", {})
    chinese_b = response_b.get("systems", {}).get("chinese", {})
    tier2_a = _extract_chinese_tier2(chinese_a)
    tier2_b = _extract_chinese_tier2(chinese_b)

    assert tier2_a["strength"] is not None
    assert tier2_b["strength"] is not None
    assert (
        tier2_a["strength"] != tier2_b["strength"]
        or tier2_a["favourable"] != tier2_b["favourable"]
        or tier2_a["dominant"] != tier2_b["dominant"]
    )

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


def test_profile_compute_emits_core_schema():
    payload = {
        "name": "Example Person",
        "birth": {
            "date": "1999-02-26",
            "time": "14:00:00",
            "timezone": "UTC",
            "location": {
                "city": "Hyderabad",
                "region": "Telangana",
                "country": "India",
                "lat": 0,
                "lon": 0,
            },
        },
    }

    if _HAS_TESTCLIENT:
        client = TestClient(app)
        response = client.post("/profile/compute", json=payload)
        assert response.status_code == 200
        response_json = response.json()
    else:
        model = ProfileComputeRequest.model_validate(payload)
        response_json = compute_profile(model)

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
    validator.validate(response_json)

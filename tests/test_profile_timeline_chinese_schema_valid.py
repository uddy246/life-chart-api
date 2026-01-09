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
from life_chart_api.routes.profile_timeline import TimelineRequest, get_timeline


def _timeline_registry(schema_path: Path) -> Registry:
    cycle_path = schema_path.parent / "cycle.schema.json"

    def load_resource(path: Path, contents: dict | None = None):
        uri = path.resolve().as_uri()
        if contents is None:
            contents = json.loads(path.read_text(encoding="utf-8"))
        return uri, Resource.from_contents(contents)

    timeline_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    timeline_schema["$id"] = schema_path.resolve().as_uri()
    cycle_schema = json.loads(cycle_path.read_text(encoding="utf-8"))
    cycle_schema["$id"] = cycle_path.resolve().as_uri()

    return Registry().with_resources(
        [
            load_resource(schema_path, timeline_schema),
            load_resource(cycle_path, cycle_schema),
        ]
    )


def _get_timeline(params: dict) -> dict:
    if _HAS_TESTCLIENT:
        client = TestClient(app)
        response = client.get("/profile/timeline", params=params)
        assert response.status_code == 200
        return response.json()
    model = TimelineRequest.model_validate(params)
    return get_timeline(model)


def test_profile_timeline_chinese_schema_valid():
    params = {
        "name": "Example Person",
        "date": "1999-02-26",
        "time": "14:00:00",
        "timezone": "UTC",
        "city": "Hyderabad",
        "region": "Telangana",
        "country": "India",
        "lat": 17.385,
        "lon": 78.4867,
        "from": "2026-01",
        "to": "2027-12",
        "include": "chinese",
    }

    response_json = _get_timeline(params)

    schema_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "life_chart_api"
        / "schemas"
        / "temporal"
        / "timeline_response.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["$id"] = schema_path.resolve().as_uri()

    registry = _timeline_registry(schema_path)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema, registry=registry)
    validator.validate(response_json)

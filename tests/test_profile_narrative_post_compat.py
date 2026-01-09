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
from life_chart_api.routes.profile_narrative import (
    NarrativeRequest,
    get_narrative,
    post_narrative,
)


def _narrative_registry(schema_path: Path) -> Registry:
    def load_resource(path: Path, contents: dict | None = None):
        uri = path.resolve().as_uri()
        if contents is None:
            contents = json.loads(path.read_text(encoding="utf-8"))
        return uri, Resource.from_contents(contents)

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["$id"] = schema_path.resolve().as_uri()
    return Registry().with_resources([load_resource(schema_path, schema)])


def _get_narrative(params: dict) -> dict:
    if _HAS_TESTCLIENT:
        client = TestClient(app)
        response = client.get("/profile/narrative", params=params)
        assert response.status_code == 200
        return response.json()
    model = NarrativeRequest.model_validate(params)
    return get_narrative(model)


def _post_narrative(params: dict) -> dict:
    if _HAS_TESTCLIENT:
        client = TestClient(app)
        response = client.post("/profile/narrative", json=params)
        assert response.status_code == 200
        return response.json()
    model = NarrativeRequest.model_validate(params)
    return post_narrative(model)


def _base_params() -> dict:
    return {
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
        "include": "western,vedic,chinese",
        "granularity": "month",
    }


def test_profile_narrative_post_schema_valid():
    params = _base_params()
    response_json = _post_narrative(params)

    schema_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "life_chart_api"
        / "schemas"
        / "narrative"
        / "narrative_response.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["$id"] = schema_path.resolve().as_uri()

    registry = _narrative_registry(schema_path)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema, registry=registry)
    validator.validate(response_json)


def test_profile_narrative_post_deterministic():
    params = _base_params()
    response_a = _post_narrative(params)
    response_b = _post_narrative(params)
    assert response_a == response_b


def test_profile_narrative_post_changes_with_input():
    params_a = _base_params()
    params_b = {**_base_params(), "date": "1999-03-01", "time": "09:30:00"}
    response_a = _post_narrative(params_a)
    response_b = _post_narrative(params_b)
    assert response_a != response_b


def test_profile_narrative_post_matches_get():
    params = _base_params()
    response_get = _get_narrative(params)
    response_post = _post_narrative(params)
    assert response_get == response_post

    get_ids = [window.get("windowId") for window in response_get.get("windows", [])]
    post_ids = [window.get("windowId") for window in response_post.get("windows", [])]
    assert get_ids == post_ids

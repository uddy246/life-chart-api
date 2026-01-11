import json
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

from life_chart_api.main import app
from tests.asgi_client import call_app


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
    status, _, payload = call_app(app, "GET", "/profile/narrative", params=params)
    assert status == 200
    return payload


def _post_narrative(params: dict) -> dict:
    status, _, payload = call_app(app, "POST", "/profile/narrative", body=params)
    assert status == 200
    return payload


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
    validator.validate(response_json.get("narrative", {}))


def test_profile_narrative_post_deterministic():
    params = _base_params()
    response_a = _post_narrative(params)
    response_b = _post_narrative(params)
    assert response_a.get("narrative") == response_b.get("narrative")


def test_profile_narrative_post_changes_with_input():
    params_a = _base_params()
    params_b = {**_base_params(), "date": "1999-03-01", "time": "09:30:00"}
    response_a = _post_narrative(params_a)
    response_b = _post_narrative(params_b)
    assert response_a.get("narrative") != response_b.get("narrative")


def test_profile_narrative_post_matches_get():
    params = _base_params()
    response_get = _get_narrative(params)
    response_post = _post_narrative(params)
    assert response_get.get("narrative") == response_post.get("narrative")

    get_ids = [window.get("windowId") for window in response_get.get("narrative", {}).get("windows", [])]
    post_ids = [window.get("windowId") for window in response_post.get("narrative", {}).get("windows", [])]
    assert get_ids == post_ids

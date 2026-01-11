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


def test_profile_narrative_schema_valid():
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
        "include": "western,vedic,chinese",
        "granularity": "month",
    }

    response_json = _get_narrative(params)

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

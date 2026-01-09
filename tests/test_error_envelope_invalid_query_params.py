import json
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

from life_chart_api.main import app
from tests.asgi_client import call_app


def _error_registry(schema_path: Path) -> Registry:
    def load_resource(path: Path, contents: dict | None = None):
        uri = path.resolve().as_uri()
        if contents is None:
            contents = json.loads(path.read_text(encoding="utf-8"))
        return uri, Resource.from_contents(contents)

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["$id"] = schema_path.resolve().as_uri()
    return Registry().with_resources([load_resource(schema_path, schema)])


def test_error_envelope_invalid_query_params():
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
        "from": "2026-13",
        "to": "2027-12",
        "include": "western,vedic,chinese",
    }
    status, _, payload = call_app(app, "GET", "/profile/forecast", params=params)
    assert status == 400
    assert payload["error"]["code"] == "INVALID_INPUT"
    assert payload["error"].get("requestId")

    schema_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "life_chart_api"
        / "schemas"
        / "errors"
        / "error_response.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["$id"] = schema_path.resolve().as_uri()
    registry = _error_registry(schema_path)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema, registry=registry)
    validator.validate(payload)

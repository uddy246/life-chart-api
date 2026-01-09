import json
from pathlib import Path

import jsonschema
from referencing import Registry, Resource


def _forecast_registry(schema_path: Path) -> Registry:
    def load_resource(path: Path, contents: dict | None = None):
        uri = path.resolve().as_uri()
        if contents is None:
            contents = json.loads(path.read_text(encoding="utf-8"))
        return uri, Resource.from_contents(contents)

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["$id"] = schema_path.resolve().as_uri()

    return Registry().with_resources([load_resource(schema_path, schema)])


def test_forecast_example_validates_against_schema():
    base = Path(__file__).resolve().parents[1]
    schema_path = (
        base / "src" / "life_chart_api" / "schemas" / "temporal" / "forecast_response.schema.json"
    )
    example_path = (
        base / "src" / "life_chart_api" / "schemas" / "examples" / "temporal" / "forecast_response.example.json"
    )

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["$id"] = schema_path.resolve().as_uri()
    example = json.loads(example_path.read_text(encoding="utf-8"))

    registry = _forecast_registry(schema_path)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema, registry=registry)
    validator.validate(example)

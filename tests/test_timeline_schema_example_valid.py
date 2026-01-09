import json
from pathlib import Path

import jsonschema
from referencing import Registry, Resource


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


def test_timeline_example_validates_against_schema():
    repo_root = Path(__file__).resolve().parents[1]
    schema_path = (
        repo_root
        / "src"
        / "life_chart_api"
        / "schemas"
        / "temporal"
        / "timeline_response.schema.json"
    )
    example_path = (
        repo_root
        / "src"
        / "life_chart_api"
        / "schemas"
        / "examples"
        / "temporal"
        / "timeline_response.example.json"
    )

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["$id"] = schema_path.resolve().as_uri()
    example = json.loads(example_path.read_text(encoding="utf-8"))

    registry = _timeline_registry(schema_path)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema, registry=registry)
    validator.validate(example)

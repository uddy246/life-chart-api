import json
from pathlib import Path

import jsonschema
from referencing import Registry, Resource


def _schema_registry(schema_paths: list[Path]) -> Registry:
    resources = []
    for path in schema_paths:
        contents = json.loads(path.read_text(encoding="utf-8"))
        contents["$id"] = path.resolve().as_uri()
        resources.append((contents["$id"], Resource.from_contents(contents)))
    return Registry().with_resources(resources)


def test_all_examples_validate_against_schemas():
    base = Path(__file__).resolve().parents[1] / "src" / "life_chart_api" / "schemas"
    schema_paths = sorted(base.rglob("*.schema.json"))
    example_paths = sorted((base / "examples").rglob("*.example.json"))

    registry = _schema_registry(schema_paths)
    schema_map = {path.relative_to(base): path for path in schema_paths}

    missing = []
    for example_path in example_paths:
        rel = example_path.relative_to(base / "examples")
        schema_rel = Path(str(rel).replace(".example.json", ".schema.json"))
        schema_path = schema_map.get(schema_rel)
        if schema_path is None:
            missing.append(str(example_path))
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["$id"] = schema_path.resolve().as_uri()
        example = json.loads(example_path.read_text(encoding="utf-8"))
        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema, registry=registry)
        validator.validate(example)

    assert not missing, f"Missing schemas for examples: {', '.join(missing)}"

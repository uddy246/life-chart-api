import json
from pathlib import Path

import jsonschema
from referencing import Registry, Resource


def test_profile_response_example_validates_against_schema():
    repo_root = Path(__file__).resolve().parents[1]

    schema_path = repo_root / "src" / "life_chart_api" / "schemas" / "profile_response.schema.json"
    example_path = repo_root / "src" / "life_chart_api" / "schemas" / "examples" / "profile_response.example.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    example = json.loads(example_path.read_text(encoding="utf-8"))

    schema_dir = schema_path.parent
    schema_uri = schema_path.resolve().as_uri()
    schema_with_id = dict(schema)
    schema_with_id["$id"] = schema_uri
    western_path = schema_dir / "western_profile.schema.json"
    vedic_path = schema_dir / "vedic_profile.schema.json"
    chinese_path = schema_dir / "chinese_profile.schema.json"

    def load_resource(path: Path, contents: dict | None = None):
        uri = path.resolve().as_uri()
        if contents is None:
            contents = json.loads(path.read_text(encoding="utf-8"))
        return uri, Resource.from_contents(contents)

    # Register sibling schemas so local $ref lookups stay on disk.
    registry = Registry().with_resources(
        [
            load_resource(schema_path, schema_with_id),
            load_resource(western_path),
            load_resource(vedic_path),
            load_resource(chinese_path),
        ]
    )

    validator_cls = jsonschema.validators.validator_for(schema_with_id)
    validator = validator_cls(schema_with_id, registry=registry)
    validator.validate(example)

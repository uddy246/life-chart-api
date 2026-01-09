import json
from pathlib import Path

import jsonschema


def test_vedic_profile_example_validates_against_schema():
    repo_root = Path(__file__).resolve().parents[1]

    schema_path = (
        repo_root
        / "src"
        / "life_chart_api"
        / "schemas"
        / "vedic_profile.schema.json"
    )
    example_path = (
        repo_root
        / "src"
        / "life_chart_api"
        / "schemas"
        / "examples"
        / "vedic_profile.example.json"
    )

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    example = json.loads(example_path.read_text(encoding="utf-8"))

    try:
        jsonschema.validate(instance=example, schema=schema)
    except jsonschema.ValidationError as e:
        print("SCHEMA VALIDATION ERROR:")
        print(e.message)
        print("PATH:", list(e.path))
        print("SCHEMA PATH:", list(e.schema_path))
        raise


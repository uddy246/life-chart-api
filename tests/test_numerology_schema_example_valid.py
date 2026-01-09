import json
from pathlib import Path

import jsonschema


def test_numerology_example_validates_against_schema():
    repo_root = Path(__file__).resolve().parents[1]
    schema_path = repo_root / "src" / "life_chart_api" / "schemas" / "numerology.schema.json"
    example_path = repo_root / "src" / "life_chart_api" / "schemas" / "examples" / "numerology.example.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    example = json.loads(example_path.read_text(encoding="utf-8"))

    jsonschema.validate(instance=example, schema=schema)

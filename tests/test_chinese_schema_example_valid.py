import json
from pathlib import Path

import jsonschema


def test_chinese_profile_example_validates_against_schema():
    repo_root = Path(__file__).resolve().parents[1]

    schema_path = repo_root / "src" / "life_chart_api" / "schemas" / "chinese_profile.schema.json"
    example_path = repo_root / "src" / "life_chart_api" / "schemas" / "examples" / "chinese_profile.example.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    example = json.loads(example_path.read_text(encoding="utf-8"))

    jsonschema.validate(instance=example, schema=schema)

from __future__ import annotations

import json
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


def _package_version() -> str:
    try:
        return version("life-chart-api")
    except PackageNotFoundError:
        return "0.0.0"


def load_example_json(filename: str) -> dict[str, Any]:
    examples_dir = Path(__file__).resolve().parent / "examples"
    path = examples_dir / filename
    return json.loads(path.read_text(encoding="utf-8"))


def stamp_meta_and_input(doc: dict[str, Any], name: str, birth: dict[str, Any]) -> dict[str, Any]:
    meta = doc.get("meta")
    if isinstance(meta, dict):
        engine = meta.setdefault("engine", {})
        meta["generatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        meta.setdefault("schemaVersion", "1.0.0")
        meta.setdefault("locale", "en-GB")
        engine["name"] = "life-chart-api"
        engine["version"] = _package_version()

    input_block = doc.get("input")
    if isinstance(input_block, dict):
        input_block["name"] = name
        input_block["birth"] = birth

    return doc

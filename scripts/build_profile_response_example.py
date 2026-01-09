import json
from pathlib import Path

root = Path("src/life_chart_api/schemas/examples")
out_path = root / "profile_response.example.json"

western = json.loads((root / "western_profile.example.json").read_text(encoding="utf-8"))
vedic   = json.loads((root / "vedic_profile.example.json").read_text(encoding="utf-8"))
chinese = json.loads((root / "chinese_profile.example.json").read_text(encoding="utf-8"))

doc = {
  "meta": western["meta"],
  "input": western["input"],
  "systems": {
    "western": western,
    "vedic": vedic,
    "chinese": chinese,
    "numerology": { "note": "Numerology schema not locked yet; placeholder allowed." }
  },
  "intersection": {
    "convergences": [
      {
        "systems": ["western", "vedic"],
        "signal": "Discipline and long-term building are emphasised.",
        "confidence": 0.7,
        "note": "Example convergence.",
        "evidence": [
          { "system": "western", "key": "systems.western.strengths.dominantThemes", "note": "Theme indicates structure." },
          { "system": "vedic", "key": "systems.vedic.saturn_theme", "note": "Example linkage." }
        ]
      }
    ],
    "divergences": [],
    "bridgeTags": ["discipline", "structure", "timing"],
    "summary": {
      "headline": "Strong agreement on structured growth; timing advice differs by system.",
      "notes": ["Example note 1", "Example note 2"],
      "nextActions": ["Example action 1", "Example action 2"]
    }
  }
}

out_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
print("Wrote:", out_path)

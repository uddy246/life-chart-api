from life_chart_api.main import app
from life_chart_api.routes import profile_narrative
from tests.asgi_client import call_app


def test_profile_narrative_fallback_on_failure(monkeypatch):
    def _raise_narrative(*_args, **_kwargs):
        raise RuntimeError("narrative failed")

    monkeypatch.setattr(profile_narrative, "build_narrative_response", _raise_narrative)

    params = {"name": "Ada Lovelace", "dob": "1990-01-01"}
    status, _, payload = call_app(app, "GET", "/profile/narrative", params=params)
    assert status == 200
    assert "profile" in payload
    assert "intersection" in payload
    assert "narrative" in payload

    narrative = payload.get("narrative", {})
    assert narrative.get("windows") == []
    overview = narrative.get("overview", {})
    assert overview.get("headline") == "Narrative unavailable."

    warnings = payload.get("profile", {}).get("warnings", [])
    assert "narrative_unavailable" in warnings

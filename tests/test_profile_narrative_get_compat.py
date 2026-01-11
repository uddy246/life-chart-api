from life_chart_api.main import app
from tests.asgi_client import call_app


def _assert_envelope(payload: dict) -> None:
    assert "profile" in payload
    assert "intersection" in payload
    assert "narrative" in payload


def test_profile_narrative_get_compat_query_and_flat():
    query_params = {"query.name": "Ada Lovelace", "query.dob": "1990-01-01"}
    status, _, payload = call_app(app, "GET", "/profile/narrative", params=query_params)
    assert status == 200
    _assert_envelope(payload)

    flat_params = {"name": "Ada Lovelace", "dob": "1990-01-01"}
    status, _, payload = call_app(app, "GET", "/profile/narrative", params=flat_params)
    assert status == 200
    _assert_envelope(payload)

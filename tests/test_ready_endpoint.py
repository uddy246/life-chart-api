from life_chart_api.main import app
from tests.asgi_client import call_app


def test_ready_endpoint():
    status, _, payload = call_app(app, "GET", "/ready")
    assert status == 200
    assert payload["status"] == "ready"
    assert payload["version"]
    assert payload["checks"]["schemasLoaded"] is True

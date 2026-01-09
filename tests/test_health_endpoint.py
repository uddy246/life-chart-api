from life_chart_api.main import app
from tests.asgi_client import call_app


def test_health_endpoint():
    status, _, payload = call_app(app, "GET", "/health")
    assert status == 200
    assert payload == {"status": "ok"}

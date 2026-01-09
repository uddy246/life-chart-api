from life_chart_api.main import app
from tests.asgi_client import call_app


def test_metrics_endpoint():
    status, _, payload = call_app(app, "GET", "/metrics")
    assert status == 200
    assert "requests" in payload
    assert "errors" in payload
    assert "latency_ms" in payload

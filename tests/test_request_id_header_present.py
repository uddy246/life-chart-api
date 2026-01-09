from life_chart_api.main import app
from tests.asgi_client import call_app


def test_request_id_header_present():
    status, headers, _ = call_app(app, "GET", "/health")
    assert status == 200
    assert headers.get("x-request-id")

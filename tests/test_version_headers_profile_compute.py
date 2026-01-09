from life_chart_api.main import app
from tests.asgi_client import call_app


def test_version_headers_profile_compute():
    payload = {
        "name": "Example Person",
        "birth": {
            "date": "1999-02-26",
            "time": "14:00:00",
            "timezone": "UTC",
            "location": {
                "city": "Hyderabad",
                "region": "Telangana",
                "country": "India",
                "lat": 17.385,
                "lon": 78.4867,
            },
        },
    }
    status, headers, _ = call_app(app, "POST", "/profile/compute", body=payload)
    assert status == 200
    assert headers.get("x-api-version")
    assert headers.get("x-schema-version")

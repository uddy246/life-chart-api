def test_error_envelope_internal_error():
    from life_chart_api.main import handle_unhandled
    import json

    class DummyState:
        request_id = "test-request-id"

    class DummyRequest:
        state = DummyState()

    response = handle_unhandled(DummyRequest(), RuntimeError("boom"))
    assert response.status_code == 500
    payload = json.loads(response.body.decode("utf-8"))
    assert payload["error"]["code"] == "INTERNAL_ERROR"
    assert payload["error"]["requestId"] == "test-request-id"

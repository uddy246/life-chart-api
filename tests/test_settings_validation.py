import pytest

from life_chart_api.settings import load_settings


def test_settings_validation_invalid_env(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MIN", "bad")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    with pytest.raises(RuntimeError):
        load_settings()


def test_settings_validation_valid_env(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MIN", "120")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    settings = load_settings()
    assert settings.RATE_LIMIT_PER_MIN == 120

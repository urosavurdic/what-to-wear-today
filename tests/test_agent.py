"""
Tests run without network access or API keys.

Everything that would reach out is patched, which is only possible because
the modules no longer fetch anything at import time.
"""
import pytest

import util
from weather_parse import MissingAPIKeys, WeatherParser, load_api_keys


@pytest.fixture(autouse=True)
def clear_context_cache():
    """Stops a context looked up in one test leaking into the next."""
    util._context = None
    yield
    util._context = None


@pytest.mark.parametrize("message", [
    "Do I need an umbrella?",
    "What should I WEAR today?",
    "is it cold outside",
])
def test_detects_weather_messages(message):
    assert util.is_weather_related(message) is True


@pytest.mark.parametrize("message", ["Who won the match?", "Tell me a joke."])
def test_ignores_unrelated_messages(message):
    assert util.is_weather_related(message) is False


def test_load_api_keys_names_what_is_missing(monkeypatch):
    for var in ["OPENWEATHER_API_KEY", "GROQ_API_KEY", "IPINFO_API_KEY"]:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr("weather_parse.load_dotenv", lambda *a, **kw: False)

    with pytest.raises(MissingAPIKeys) as excinfo:
        load_api_keys()
    assert "weather" in str(excinfo.value)


def test_load_api_keys_reads_the_environment(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "w")
    monkeypatch.setenv("GROQ_API_KEY", "g")
    monkeypatch.setenv("IPINFO_API_KEY", "i")
    monkeypatch.setattr("weather_parse.load_dotenv", lambda *a, **kw: False)

    assert load_api_keys() == {"weather": "w", "groq": "g", "ipinfo": "i"}


def test_filter_data_picks_the_nearest_forecast_slot():
    parser = WeatherParser(lat=44.8, lon=20.4, api_key="dummy")
    payload = {"list": [
        {"dt": 1000, "main": {"temp": 5}, "weather": [{"main": "Snow"}]},
        {"dt": 2000, "main": {"temp": 21}, "weather": [{"main": "Clear"}]},
    ]}

    result = parser._filter_data(payload, dt=1900)
    assert result["temp"] == 21
    assert result["weather_main"] == "Clear"


def test_filter_data_reports_an_empty_forecast():
    parser = WeatherParser(lat=0, lon=0, api_key="dummy")
    assert "error" in parser._filter_data({"list": []}, dt=0)


def test_fetch_returns_an_error_dict_instead_of_raising(monkeypatch):
    import requests

    def boom(*args, **kwargs):
        raise requests.RequestException("network down")

    monkeypatch.setattr("weather_parse.requests.get", boom)
    result = WeatherParser(lat=0, lon=0, api_key="dummy").fetch_weather_info()
    assert result["error"] == "network down"


def test_safe_json_parse_handles_fenced_json():
    assert util.safe_json_parse('```json\n{"lat": "1"}\n```') == {"lat": "1"}


def test_safe_json_parse_falls_back_on_garbage():
    assert util.safe_json_parse("not json at all", fallback={"ok": True}) == {"ok": True}


def test_context_is_fetched_once_and_cached(monkeypatch):
    calls = []

    def fake_context():
        calls.append(1)
        return {"lat": "1", "lon": "2", "timestamp": 0, "weekday": "Monday"}

    monkeypatch.setattr(util, "contextual_data", fake_context)
    util.get_context()
    util.get_context()
    assert len(calls) == 1


def test_importing_util_does_not_hit_the_network(monkeypatch):
    # The original module called ipinfo.io at import time; guard against regressing.
    def boom(*args, **kwargs):
        raise AssertionError("network call at import time")

    monkeypatch.setattr("util.requests.get", boom)
    import importlib
    importlib.reload(util)

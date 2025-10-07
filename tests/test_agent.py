import pytest
from weather_parse import WeatherParser

class DummyParser:
    def fetch_weather_info(self):
        return {"temp": 22, "weather_main": "Clear"}

def test_is_weather_related(monkeypatch):
    bot = WeatherParser(lat=44.8, lon=20.4)
    monkeypatch.setattr("weather_parse.WeatherParser", lambda *a, **kw: DummyParser())
    monkeypatch.setattr("util.ask_groq", lambda prompt: "It's sunny!")
    response = bot.fetch_weather_info()
    assert "clouds" in response

def test_non_weather_message(monkeypatch):
    monkeypatch.setattr("util.ask_groq", lambda prompt: "Hello there!")
    from util import ask_groq
    response = ask_groq("Hi!")

    assert "hello" in response.lower()
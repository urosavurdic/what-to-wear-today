import os
from datetime import datetime

import requests
from dotenv import load_dotenv

FORECAST_URL = "https://pro.openweathermap.org/data/2.5/forecast/hourly"


class MissingAPIKeys(RuntimeError):
    """Raised when the environment does not carry the keys the app needs."""


def load_api_keys():
    """
    Reads the three API keys from the environment, loading a .env first if
    one is present.

    Called at use time rather than import time: importing this module must
    not require credentials, or the tests and any offline use break.
    """
    load_dotenv()
    keys = {
        "weather": os.getenv("OPENWEATHER_API_KEY"),
        "groq": os.getenv("GROQ_API_KEY"),
        "ipinfo": os.getenv("IPINFO_API_KEY"),
    }
    missing = [name for name, value in keys.items() if not value]
    if missing:
        raise MissingAPIKeys(
            f"Missing API key(s): {', '.join(missing)}. "
            f"Copy .env.example to .env and fill them in."
        )
    return keys


class WeatherParser:
    """Fetches an hourly forecast for one place and trims it to what the bot needs."""

    def __init__(self, lat: float, lon: float, dt: int = None, api_key: str = None):
        """
        Args:
            lat: latitude
            lon: longitude
            dt: UNIX timestamp to report for; defaults to now
            api_key: overrides the key from the environment, for tests
        """
        self.lat = lat
        self.lon = lon
        self._api_key = api_key
        self.current_datetime = int(datetime.now().timestamp())
        self.dt = dt if dt is not None else self.current_datetime

    @property
    def api_key(self):
        if self._api_key is None:
            self._api_key = load_api_keys()["weather"]
        return self._api_key

    def fetch_weather_info(self):
        """Returns the forecast entry closest to self.dt, or an {'error': ...} dict."""
        params = {
            "lat": self.lat,
            "lon": self.lon,
            "units": "metric",
            "appid": self.api_key,
        }
        try:
            response = requests.get(FORECAST_URL, params=params, timeout=10)
            response.raise_for_status()
            return self._filter_data(response.json(), self.dt)
        except requests.RequestException as exc:
            return {"error": str(exc)}

    def _filter_data(self, data, dt):
        """Picks the forecast slot nearest dt and keeps the fields the prompt uses."""
        entries = data.get("list") or []
        if not entries:
            return {"error": "no forecast entries returned"}

        nearest = min(entries, key=lambda e: abs(e["dt"] - dt))
        main = nearest.get("main", {})
        weather = (nearest.get("weather") or [{}])[0]
        return {
            "dt": nearest["dt"],
            "temp": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "humidity": main.get("humidity"),
            "weather_main": weather.get("main"),
            "description": weather.get("description"),
            "wind_speed": nearest.get("wind", {}).get("speed"),
            "rain_3h": nearest.get("rain", {}).get("3h", 0),
        }

import requests
from datetime import datetime
from dotenv import load_dotenv
import os

def load_api_keys():
    loaded = load_dotenv()
    if not loaded:
        raise Exception("Could not load .env file")
    else:
        return {
            os.getenv("OPENWEATHER_API_KEY"),
            os.getenv("GROQ_API_KEY"),
            os.getenv("IPINFO_API_KEY"),
        }

api_key, _, _ = load_api_keys()

class WeatherParser:
    def __init__(self, lat: float, lon: float, dt: int = None):
        """
        Initialize with API key and coordinates.
        
        Args:
            api_key: OpenWeatherMap API key
            lat: Latitude
            lon: Longitude
            dt: UNIX timestamp (optional, defaults to now)
        """
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self.current_datetime = int(datetime.now().timestamp())
        self.dt = dt if dt is not None else self.current_datetime
        
        # Determine task type
        self.task_type = self._determine_task_type()
    
    def _determine_task_type(self) -> str:
        """Determine whether to fetch current, forecast, or historical data"""
        time_diff = self.dt - self.current_datetime
        
        if abs(time_diff) < 3600:  # Within 1 hour = current
            return 'now'
        elif time_diff > 0 and time_diff <= 5 * 86400:  # Future, within 5 days
            return '5_days'
        elif time_diff > 5 * 86400:  # Future, beyond 5 days
            return 'future_long'  # Not supported by free API
        else:  # Past
            return 'past'
    
    def get_weather_now(self) -> dict:
        """Fetch current weather"""
        url = "https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}"

        response = requests.get(url)
        return response.json()
    
    def get_weather_5_days(self, units: str = "metric") -> dict:
        """Fetch 5-day forecast (3-hour intervals)"""
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.api_key,
            "units": units
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_weather_past(self, units: str = "metric") -> dict:
        """Fetch historical weather (requires Time Machine subscription)"""
        url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
        params = {
            "lat": self.lat,
            "lon": self.lon,
            "dt": self.dt,
            "appid": self.api_key,
            "units": units
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_weather(self) -> dict:
        """Fetch weather based on automatically determined task type"""
        if self.task_type == 'now':
            return self.get_weather_now()
        elif self.task_type == '5_days':
            return self.get_weather_5_days()
        elif self.task_type == 'past':
            return self.get_weather_past()
        else:
            raise ValueError(f"Task type '{self.task_type}' not supported with free API")
    
    def __repr__(self):
        return f"Weather(lat={self.lat}, lon={self.lon}, task_type='{self.task_type}')"


# Test it:
dt = int(datetime(2025, 10, 8, 12, 0).timestamp())  # Example past date
print(dt)
w = WeatherParser("8d11b60e3725dc9d8929ae743be16838", 44.8176, 20.4569)
data = w.get_weather()
print(data)
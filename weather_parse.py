import requests
from datetime import datetime
from dotenv import load_dotenv
import os

def load_api_keys():
    loaded = load_dotenv()
    if not loaded:
        raise Exception("Could not load .env file")

    keys = {

        'weather': os.getenv("OPENWEATHER_API_KEY"),
        'groq': os.getenv("GROQ_API_KEY"),
        'ipinfo': os.getenv("IPINFO_API_KEY"),
    }
    return keys

api_key = load_api_keys()["weather"]

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
        elif time_diff > 86400:
            return 'future'
        else:  # Past
            return 'past'
    
    def get_weather_now(self) -> dict:
        """Fetch current weather"""
        url = "https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&appid={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical weather: {e}")
            return {}
    
    def get_weather_future(self) -> dict:
        """Fetch 5-day forecast (3-hour intervals)"""
        url = f"https://api.openweathermap.org/data/2.5/forecast/daily?lat={self.lat}&lon={self.lon}&cnt=16&units=metric&appid={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            filtered_data = filter_data(data)
            return filtered_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical weather: {e}")
            return {}
    
    def get_weather_past(self) -> dict:
        """Fetch historical weather (requires Time Machine subscription)"""
        end = dt + 86400
        url = f"https://history.openweathermap.org/data/2.5/history/city?lat={self.lat}&lon={self.lon}&type=hour&start={dt}&end={end}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical weather: {e}")
            return {}
    
    def get_weather(self) -> dict:
        """Fetch weather based on automatically determined task type"""
        if self.task_type == 'now':
            return self.get_weather_now()
        elif self.task_type == '5_days':
            return self.get_weather_future()
        elif self.task_type == 'past':
            return self.get_weather_past()
        else:
            raise ValueError(f"Task type '{self.task_type}' not supported with free API")
    
    def __repr__(self):
        return f"Weather(lat={self.lat}, lon={self.lon}, task_type='{self.task_type}')"


def filter_data(data):
    return data

# Test it:
dt = int(datetime(2025, 10, 7, 19, 0).timestamp())  # Example past date
print(dt)
print(api_key)
w = WeatherParser(44.8176, 20.4569, dt)
data = w.get_weather()
print(data)
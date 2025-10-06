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
            lat: Latitude
            lon: Longitude
            dt: UNIX timestamp (optional, defaults to now)
        """
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self.current_datetime = int(datetime.now().timestamp())
        self.dt = dt if dt is not None else self.current_datetime

    def fetch_weather_info(self):
        #Fetch current weather
        url = f"https://pro.openweathermap.org/data/2.5/forecast/hourly?lat={self.lat}&lon={self.lon}&units=metric&appid={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            filtered_data = self._filter_data(data, self.dt)
            return filtered_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather now: {e}")
            return {}
    
    def _filter_data(self, data, dt):
        # Find the closest forecast
        closest_entry = min(data["list"], key=lambda x: abs(x["dt"] - dt))
        weather_info = {
            "feels_like": closest_entry["main"]["feels_like"],
            "temp": closest_entry["main"]["temp"],
            "temp_min": closest_entry["main"]["temp_min"],
            "temp_max": closest_entry["main"]["temp_max"],
            "pressure": closest_entry["main"]["pressure"],
            "humidity": closest_entry["main"]["humidity"],
            "weather_main": closest_entry["weather"][0]["main"],
            "weather_description": closest_entry["weather"][0]["description"],
            "clouds": closest_entry["clouds"]["all"],
            "wind_speed": closest_entry["wind"]["speed"],
            "rain_1h": closest_entry.get("rain", {}).get("1h", 0),
            "snow_1h": closest_entry.get("snow", {}).get("1h", 0),
            "pop": closest_entry.get("pop", 0),
            "city_sunrise": data["city"]["sunrise"],
            "city_sunset": data["city"]["sunset"]
        }

        return weather_info
                            
        
    def __repr__(self):
        return f"Weather(lat={self.lat}, lon={self.lon}')"

#dt = int(datetime(2026, 6, 10, 21, 13).timestamp())  # Example past date
dt = datetime.now().timestamp() + 86402
#print(dt)
print(api_key)
w = WeatherParser(44.8176, 20.4569)
data = w.fetch_weather_info()
print(data)   


"""
# Initial idea was to make weather data available over all time. But that makes problem more complex, especially for MVP. So I will proceed building chatbot that is able to see weather 4 days in advnce
    def _determine_task_type(self) -> str:
        #Determine whether to fetch current, forecast, or historical data
        time_diff = self.dt - self.current_datetime
        
        if abs(time_diff) <= 3600:  # Within 1 hour = current
            return 'now'
        elif time_diff >= (86400*16):
            raise ValueError("OpenWeather does not contain data that much in the future")
        elif time_diff > 86400 and time_diff < (86400*16):
            return 'future'
        else:  # Past
            return 'past'
    
    def get_weather_now(self) -> dict:
        #Fetch current weather
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={self.lat}&lon={self.lon}&units=metric&appid={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            filtered_data = filter_data(data)
            return filtered_data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather now: {e}")
            return {}
    
    def get_weather_future(self) -> dict:
        #Getting forcast for next 16 days
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
        #Fetch historical weather (requires Time Machine subscription)
        end = self.dt + 86400
        url = f"https://history.openweathermap.org/data/2.5/history/city?lat={self.lat}&lon={self.lon}&type=hour&start={self.dt}&end={end}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            filtered_data = filter_data(data)
            return filtered_data
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical weather: {e}")
            return {}
    
    def get_weather(self) -> dict:
        #Fetch weather based on automatically determined task type
        if self.task_type == 'now':
            return self.get_weather_now()
        elif self.task_type == 'future':
            return self.get_weather_future()
        elif self.task_type == 'past':
            return self.get_weather_past()
        else:
            raise ValueError(f"Task type '{self.task_type}' not supported with free API")


"""    

    

# Test it:



# Weather Chatbot

**Goal:**  
This app is a chatbot that provides users with weather-related suggestions.  
It’s the MVP version. In the future, it could be extended to provide more information like transportation tips, travel advice, or even event planning.

## Files

- `experiment.ipynb` - Early experiments and API testing  
- `weather_parse.py` - Fetches relevant weather data from OpenWeatherMap  
- `main.py` - Main loop for chatbot interactions  
- `util.py` - Helper functions  
- `tests/` - Pytest tests to ensure code works  

## Features

- Chat with the bot about weather in any location  
- Accepts optional date input (uses today’s date by default)  
- Provides current weather and short-term forecasts  
- Suggests outfits, activities, and practical advice  

## API Keys

This project requires API keys for some services. You need to sign up for these services and create your own keys:

- OpenWeatherMap: [https://openweathermap.org/api](https://openweathermap.org/api)  
- GROQ API: [https://groq.com/](https://groq.com/)  
- IPINFO: [https://ipinfo.io/](https://ipinfo.io/)

### Setup API keys

Here is the example of the format of `.env` file:

OPENWEATHER_API_KEY=**************************

GROQ_API_KEY=*************************************

IPINFO_API_KEY =*********************

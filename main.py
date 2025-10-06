import requests
from groq import Groq
from .util import load_api_keys

import json
from .weather import WeatherParser

OPENWEATHER_API_KEY, GROQ_API_KEY, _ = load_api_keys()








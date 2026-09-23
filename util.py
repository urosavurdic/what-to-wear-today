import json
from datetime import datetime

import requests
from openai import OpenAI

from weather_parse import load_api_keys

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-20b"

_context = None

WEATHER_KEYWORDS = [
    "weather", "temperature", "rain", "snow", "sunny", "cloudy", "forecast", "hot",
    "cold", "warm", "cool", "humidity", "wind", "storm", "umbrella", "jacket", "coat",
    "outside", "outdoor", "today", "tomorrow", "weekend", "dress", "wear", "bring",
]


def contextual_data():
    """Looks up the caller's approximate location and the current time."""
    token = load_api_keys()["ipinfo"]
    response = requests.get(f"https://ipinfo.io/json?token={token}", timeout=10)
    response.raise_for_status()
    loc = response.json()
    lat, lon = loc["loc"].split(",")
    return {
        "timestamp": datetime.now().timestamp(),
        "weekday": datetime.now().strftime("%A"),
        "lat": lat,
        "lon": lon,
    }


def get_context():
    """
    Returns the cached location/time context, looking it up on first use.

    Deliberately not computed at import time: that fired a network call
    just to import this module, which broke offline use and the tests.
    """
    global _context
    if _context is None:
        _context = contextual_data()
    return _context


def is_weather_related(text: str) -> bool:
    """True if the message looks like it is about the weather."""
    lowered = text.lower()
    return any(word in lowered for word in WEATHER_KEYWORDS)


def ask_groq(prompt: str) -> str:
    """Sends one prompt to the model and returns the reply text."""
    client = OpenAI(api_key=load_api_keys()["groq"], base_url=GROQ_BASE_URL)
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful weather assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_completion_tokens=8192,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content.strip()


def safe_json_parse(response_text: str, fallback=None):
    """
    Pulls JSON out of a model reply, tolerating ```json fences.

    Falls back to the current context if the reply is not usable, so a
    malformed response degrades to 'here' rather than raising.
    """
    try:
        text = response_text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text)
    except (ValueError, IndexError):
        return fallback if fallback is not None else get_context()


def extract_context_via_llm(user_input: str):
    """Asks the model to pull a place and time out of the message."""
    context = get_context()
    prompt = f"""
    Extract time and location from the context of this user message.

    Current date/time: {context["timestamp"]}
    Base location: {context["lat"]} {context["lon"]}

    User said: "{user_input}"

    Return valid JSON ONLY:
    {{
        "timestamp": <unix timestamp>,
        "lat": "<latitude or null>",
        "lon": "<longitude or null>"
    }}
    """
    return safe_json_parse(ask_groq(prompt))


def generate_weather_response(user_input: str, weather_data: dict, previous_chat: str):
    """Turns the forecast into a short, practical answer."""
    context = get_context()
    prompt = f"""
    You are a friendly assistant that gives helpful, practical weather advice.

    Weather Data:
    {json.dumps(weather_data, indent=2)}

    Context:
    - Latitude: {context.get('lat')}
    - Longitude: {context.get('lon')}
    - Time: {context.get('timestamp')}
    User said: "{user_input}"

    Conversation so far:
    {previous_chat if previous_chat else "None"}

    Give a natural, friendly, concise answer: summarize the weather and suggest
    something practical (what to wear, do, or avoid).
    """
    return ask_groq(prompt)

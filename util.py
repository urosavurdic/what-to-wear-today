import os
from datetime import datetime
import requests
from openai import OpenAI
import json
from .weather import WeatherParser, load_api_keys


def contextual_data():
    _, _, IPINFO_url = load_api_keys()["ipinfo"]
    response = requests.get(IPINFO_url)
    loc = response.json()
    data = {
        "timestamp": datetime.now().timestamp(), # Current timestamp in seconds
        "weekday": datetime.now().strftime("%A"), # Full weekday name
        "lat": loc["loc"].split(",")[0],
        "lon": loc["loc"].split(",")[1],
    }
    return data

context = contextual_data()

def is_weather_related(text: str) -> bool:
    """Detect if user query relates to weather"""
    keywords = [
        "weather", "temperature", "rain", "snow", "sunny", "cloudy", "forecast", "hot",
        "cold", "warm", "cool", "humidity", "wind", "storm", "umbrella", "jacket", "coat",
        "outside", "outdoor", "today", "tomorrow", "weekend", "dress", "wear", "bring"
    ]
    text_lower = text.lower()
    return any(k in text_lower for k in keywords)

def ask_groq(prompt: str) -> str:
    _, GROQ_API_KEY, _ = load_api_keys()["groq"]

    client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    )
    
    completion = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": ""}],
    temperature=1,
    max_completion_tokens=8192,
    top_p=1,
    reasoning_effort="medium",
    stream=True,
    stop=None
    )

    return completion.choices[0].message.content.strip()

def safe_json_parse(response_text: str):
    """Extract JSON safely from LLM response"""
    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        return json.loads(response_text)
    except Exception:
        return context


def extract_context_via_llm(user_input: str):
    prompt = f"""
    Extract time and location from the context of this user message.

    Current date/time: {context["timestamp"]}
    Base location: {context["lat"]} {context["lon"]}

    User said: "{user_input}"

    Return valid JSON ONLY:
    {{
        "timestamp": <unix timestamp>,
        "lat": "<latitude or null>",
        "lon": "<longitude or null>",
    }}
    """

    response = ask_groq(prompt)
    return safe_json_parse(response)

def generate_weather_response(user_input: str, weather_data: dict, previous_chat: str):
    """LLM generates natural weather-aware answer"""
    prompt = f"""
    You are a friendly assistant that gives helpful, practical weather advice.

    Weather Data:
    {json.dumps(weather_data, indent=2)}

    Context:
    - Latitude: {context.get('lat')}
    - Lonfitude: {context.get('lon')}
    - Time: {context.get('timestamp')}
    User said: "{user_input}"

    Conversation so far:
    {previous_chat if previous_chat else "None"}

    Give a natural, friendly, concise answer: summarize the weather and suggest something practical (what to wear, do, or avoid).
    """
    return ask_groq(prompt)  
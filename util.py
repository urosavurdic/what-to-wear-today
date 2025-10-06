from dotenv import load_dotenv
import os
from datetime import datetime
import requests
from openai import OpenAI
import json
from .weather import WeatherParser

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

def contextual_data():
    _, _, IPINFO_url = load_api_keys()
    response = requests.get(IPINFO_url)
    loc = response.json()
    data = {
        "timestamp": datetime.now().timestamp(), # Current timestamp in seconds
        "weekday": datetime.now().strftime("%A"), # Full weekday name
        "lat": loc["loc"].split(",")[0],
        "lon": loc["loc"].split(",")[1],
    }
    return data

weather_data = ""

instructions = {
    "Respond me with only 0 or 1 if a user talks about anything that might influence his behaviours, choices or actions based on weather conditions" : 0,
    "Continue with conversation, respond however you believe it's the best" : 1,
    f"Currently timestamp is {contextual_data().timestamp}, weekday {contextual_data().weekday} and loging latitude and longitude are {contextual_data().lat} and {contextual_data().lon}, respectively. Based on those information and what user said, figure out what timestamp, latitude and longitude is reffering to, and return the values in json format where keys are timestamp, lat and lon" : 2,
    f"Based on weather data and users info try to form informative that will give user overview of weather in a given moment and place and suggest user an action, choice or behaviour based on weather (ex: weather summary, clothing suggestion, transportation typa for that day, health advice, how to spent their free time based on weather and location or anything else that comes to your mind) {weather_data}" : 3,

}
def ask_groq(user_input: str, instructions: str, previous_chat: str = None) -> str:
    _, GROQ_API_KEY, _ = load_api_keys()

    client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    )
    prompt = instructions + "\nUser: " + user_input + (f"\nPrevious chat: {previous_chat}" if previous_chat else "")
    response = client.responses.create(
    input=prompt,
    model="openai/gpt-oss-20b",
    )
    return response.output_text

def chat_bot_loop():
    print("Welcome to the Weather Chatbot! How can I assist you today?")
    previous_chat = ""
    stage = 0  # Start with the first instruction
    while previous_chat.len() < 1000:  # Limit the chat history to the last 1000 characters
        if stage != 2:
            user_input = input()
        if stage == 0:
            #response = toint(ask_groq(user_input, list(instructions.keys())[0]))
            if response:
                stage = 2  # Move to the stage for extracting contextual data
            else:
                stage = 1  # Move to the general conversation stage
                response = ask_groq(user_input, list(instructions.keys())[1], previous_chat)
                print("Chatbot:", response)
                previous_chat = (previous_chat + "\nUser: " + user_input + "\nChatbot: " + response)[-1000:]  # Keep only the last 1000 characters
        elif stage == 2: # Extract relevant contextual data
            response = ask_groq(user_input, list(instructions.keys())[2], previous_chat)
            try:
                data = json.loads(response)
                lat = data.get("lat", contextual_data().lat, None)
                lon = data.get("lon", contextual_data().lon, None)
                timestamp = data.get("timestamp", contextual_data().timestamp, None)
                # Fetch weather data based on extracted context
                weather_data = WeatherParser(lat, lon, timestamp).get_weather()
                stage = 3  # Move to the weather-informed response stage
            except json.JSONDecodeError:
                print("Chatbot: Sorry, I couldn't extract the necessary information. Let's continue our conversation.")
                stage = 1  # Fallback to general conversation
        elif stage == 3: # Weather-informed response
                response = ask_groq(user_input, list(instructions.keys())[3].format(weather_data=weather_data), previous_chat)
                print("Chatbot:", response)
                previous_chat = (previous_chat + "\nUser: " + user_input + "\nChatbot: " + response)[-1000:]  # Keep only the last 1000 characters

        else:
            print("Invalid stage. Resetting to initial stage.")
            stage = 0

    print("Character limit reached. Thank you for using the Weather Chatbot. Refresh the page to start a new session.")


    


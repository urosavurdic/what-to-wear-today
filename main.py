from util import (
    ask_groq,
    extract_context_via_llm,
    generate_weather_response,
    get_context,
    is_weather_related,
)
from weather_parse import WeatherParser

MAX_HISTORY_CHARS = 1000


def chat_bot_loop():
    print("Welcome to your Weather Chatbot!")
    print("Ask me anything, or type exit.")
    previous_chat = ""

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Chatbot: Thank you for talking about weather!")
            break
        if not user_input:
            continue

        if is_weather_related(user_input):
            # Pull the place and time out of the message, then fetch for those
            extracted = extract_context_via_llm(user_input)
            weather_data = WeatherParser(
                extracted["lat"], extracted["lon"], extracted["timestamp"]
            ).fetch_weather_info()
            response = generate_weather_response(user_input, weather_data, previous_chat)
        else:
            context = get_context()
            context_info = (
                f"\nContext: The user is at latitude {context['lat']}, "
                f"longitude {context['lon']}, local timestamp {context['timestamp']}, "
                f"and it is {context['weekday']}."
            )
            if previous_chat:
                context_info += f"\nPrevious conversation:\n{previous_chat[-500:]}"
            response = ask_groq(
                f"{context_info}\n\nUser said: {user_input}\n\nRespond naturally and helpfully."
            )

        print("Chatbot:", response)
        previous_chat = (
            previous_chat + f"\nUser: {user_input}\nChatbot: {response}"
        )[-MAX_HISTORY_CHARS:]


if __name__ == "__main__":
    chat_bot_loop()

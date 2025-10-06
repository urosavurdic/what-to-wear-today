from .weather import WeatherParser
from .util import is_weather_related, ask_groq, extract_context_via_llm, generate_weather_response

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

        # detect intent

        if not is_weather_related(user_input):
            response = ask_groq("You are a general assistant. Respond naturally to: {user_input}")
            print("Chatbot:", response)
        
        else: # weather related topic -> extract context(location/time)
            extracted_context = extract_context_via_llm(user_input)

            # collecting and filtering weather data from OpenWeather
            try:
                weather_data = WeatherParser(
                    extracted_context["lat"],
                    extracted_context["lon"],
                    extracted_context["timestamp"]
                ).get_weather()
            except Exception as e:
                print("Chatbot: I couldn’t fetch live weather, but let’s still chat about it! Could you describe me your situation more?")
                weather_data = {"error": str(e)}
            
            response = generate_weather_response(user_input, weather_data, previous_chat)
            print("Chatbot:", response)
        
        if len(previous_chat) > 8000:
            print("Chatbot: Thank you for talking with me. You've reached character limit. Reload page to start again.")
        
        previous_chat = (previous_chat + f"\nUser: {user_input}\nChatbot: {response}")[-1000:]
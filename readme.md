Goal of this app is to built a chat-bot that can give user a weather related suggestions.
This is the MVP version. App could fruther be developed by giving more information to the model (ex: transportation, travel, etc.)
It consists of couple of files:
 - experiment.ipynb - early experiments and getting to know APIs
 - weather_parse.py - gets relevant data for user from OpenWeatherMap
 - weather_util.py - contains function to only keep non-redudant data (without it model would get data for multiple irrelevant days and parameters)
 - main.py - loops the whole chat, manages prompts
 - util.py - contains helper functions
 - api - contains CLI implementation
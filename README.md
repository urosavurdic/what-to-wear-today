# What to wear today

A command-line weather chatbot. Ask it anything in plain language; when the
question is about the weather it works out where and when you mean, fetches the
forecast for that place and time, and answers with practical advice rather than
a table of numbers.

```
You: do I need a jacket this evening?
Chatbot: It'll drop to about 11C after sunset with a light wind, so yes —
         something with sleeves. No rain expected, so you can skip the umbrella.
```

## What it does

- Decides whether a message is weather-related before spending an API call
- Extracts the place and time from ordinary phrasing ("tomorrow in Novi Sad")
- Falls back to your approximate location from your IP when you don't say
- Pulls the hourly forecast slot nearest the time you asked about
- Keeps recent turns as context so follow-up questions work

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env     # then fill in your three keys
python main.py
```

You need free API keys from [OpenWeatherMap](https://openweathermap.org/api),
[Groq](https://console.groq.com/) and [ipinfo.io](https://ipinfo.io/). Put them
in `.env` as `OPENWEATHER_API_KEY`, `GROQ_API_KEY` and `IPINFO_API_KEY`.

Run the tests (no keys or network needed):

```bash
pytest tests/
```

Or in Docker:

```bash
docker build -t what-to-wear-today .
docker run --rm -it --env-file .env what-to-wear-today
```

## How it works

`main.py` runs the chat loop. Each message is checked against a keyword list
first, which is cheap and decides whether the weather path is worth taking. On
that path the model extracts a location and timestamp, `WeatherParser` fetches
the hourly forecast and keeps the slot closest to the requested time, and the
model turns that into advice.

Credentials and the IP lookup are resolved on first use rather than at import,
so the modules import cleanly with no keys and no network — which is what lets
the tests run anywhere.

| Path | What it is |
|---|---|
| `main.py` | the chat loop |
| `util.py` | intent check, model calls, context extraction |
| `weather_parse.py` | forecast fetching and filtering |
| `tests/` | unit tests, fully mocked |
| `notebooks/` | the original API experiments |

## License

MIT — see [LICENSE](LICENSE).

from typing import Any

from tools.api_client import PublicAPIError, get_json

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    80: "rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    95: "thunderstorm",
    96: "thunderstorm with hail",
    99: "thunderstorm with heavy hail",
}


def get_current_weather(location: str) -> str:
    location = location.strip()
    if not location:
        raise PublicAPIError("Please provide a city or location.")
    if len(location) > 120:
        raise PublicAPIError("Please provide a shorter city or location name.")

    geocoding = get_json(
        GEOCODING_URL,
        {"name": location, "count": "1", "language": "en", "format": "json"},
        "Open-Meteo geocoding",
    )
    results = geocoding.get("results", [])
    if not isinstance(results, list) or not results:
        raise PublicAPIError(f"No location matched '{location}'.")

    place = results[0]
    if not isinstance(place, dict) or "latitude" not in place or "longitude" not in place:
        raise PublicAPIError("The location service returned incomplete location data.")

    forecast = get_json(
        FORECAST_URL,
        {
            "latitude": str(place["latitude"]),
            "longitude": str(place["longitude"]),
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "timezone": "auto",
        },
        "Open-Meteo weather",
    )
    current: Any = forecast.get("current")
    if not isinstance(current, dict):
        raise PublicAPIError("The weather service did not return current conditions.")

    try:
        code = int(current["weather_code"])
        description = WEATHER_CODES.get(code, f"weather code {code}")
        name = str(place["name"])
        country = place.get("country")
        place_name = f"{name}, {country}" if country else name
        temperature = current["temperature_2m"]
        apparent = current["apparent_temperature"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
    except (KeyError, TypeError, ValueError) as exc:
        raise PublicAPIError("The weather service returned incomplete current conditions.") from exc

    return (
        f"Current weather for {place_name}: {description}, {temperature}°C "
        f"(feels like {apparent}°C), humidity {humidity}%, wind {wind} km/h."
    )

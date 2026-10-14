from collections.abc import Callable

from tools.api_client import PublicAPIError
from tools.music import search_music
from tools.weather import get_current_weather

API_HANDLERS: dict[str, Callable[[str], str]] = {
    "music": search_music,
    "weather": get_current_weather,
}


def call_public_api(service: str, query: str) -> str:
    handler = API_HANDLERS.get(service.strip().lower())
    if handler is None:
        available = ", ".join(sorted(API_HANDLERS))
        raise PublicAPIError(f"'{service}' is not registered. Available services: {available}.")
    return handler(query)

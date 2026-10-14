import json
from collections.abc import Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class PublicAPIError(Exception):
    """A public API request failed or returned an unusable response."""


def get_json(endpoint: str, params: Mapping[str, str], service: str) -> dict[str, Any]:
    url = f"{endpoint}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "EmployeeServiceAgent/1.0"})
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise PublicAPIError(f"{service} returned HTTP {exc.code}.") from exc
    except (URLError, TimeoutError) as exc:
        reason = exc.reason if isinstance(exc, URLError) else "request timed out"
        raise PublicAPIError(f"{service} could not be reached: {reason}.") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublicAPIError("The service returned an invalid response.") from exc

    if not isinstance(payload, dict):
        raise PublicAPIError("The service returned an unexpected response.")
    return payload

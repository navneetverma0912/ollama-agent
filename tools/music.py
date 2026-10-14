from typing import Any

from tools.api_client import PublicAPIError, get_json

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"


def search_music(query: str) -> str:
    query = query.strip()
    if not query:
        raise PublicAPIError("Please provide a song, artist, or music search term.")
    if len(query) > 200:
        raise PublicAPIError("Please provide a shorter music search.")

    payload = get_json(
        ITUNES_SEARCH_URL,
        {"term": query, "entity": "song", "limit": "5"},
        "iTunes Search",
    )
    results: Any = payload.get("results", [])
    if not isinstance(results, list):
        raise PublicAPIError("The music service returned an unexpected results list.")
    if not results:
        return f"No songs found for '{query}'."

    entries = []
    for item in results:
        if not isinstance(item, dict):
            continue
        track = item.get("trackName")
        artist = item.get("artistName")
        if not track or not artist:
            continue
        album = item.get("collectionName")
        link = item.get("trackViewUrl")
        entry = f"- {track} — {artist}"
        if album:
            entry += f" ({album})"
        if link:
            entry += f"\n  {link}"
        entries.append(entry)

    if not entries:
        return f"No songs found for '{query}'."
    return f"Music search results for '{query}':\n" + "\n".join(entries)

import unittest
from unittest.mock import patch

from tools.api_client import PublicAPIError
from tools.music import search_music
from tools.public_apis import call_public_api
from tools.weather import get_current_weather


class PublicAPITests(unittest.TestCase):
    @patch("tools.weather.get_json")
    def test_weather_geocodes_location_and_formats_current_conditions(self, get_json):
        get_json.side_effect = [
            {"results": [{"name": "Paris", "country": "France", "latitude": 48.8, "longitude": 2.3}]},
            {"current": {
                "temperature_2m": 19,
                "apparent_temperature": 18,
                "relative_humidity_2m": 60,
                "wind_speed_10m": 8,
                "weather_code": 2,
            }},
        ]

        answer = get_current_weather(" Paris ")

        self.assertIn("Paris, France", answer)
        self.assertIn("partly cloudy", answer)
        self.assertIn("19°C", answer)
        self.assertEqual(get_json.call_count, 2)

    @patch("tools.weather.get_json", return_value={"results": []})
    def test_weather_reports_unmatched_location(self, _get_json):
        with self.assertRaisesRegex(PublicAPIError, "No location matched"):
            get_current_weather("Atlantis")

    @patch("tools.music.get_json")
    def test_music_search_formats_song_results(self, get_json):
        get_json.return_value = {"results": [{
            "trackName": "Example Song",
            "artistName": "Example Artist",
            "collectionName": "Example Album",
            "trackViewUrl": "https://example.test/song",
        }]}

        answer = search_music("Example Artist")

        self.assertIn("Example Song", answer)
        self.assertIn("Example Album", answer)
        self.assertIn("https://example.test/song", answer)

    @patch("tools.music.get_json", return_value={"results": []})
    def test_music_search_reports_no_matches(self, _get_json):
        self.assertIn("No songs found", search_music("unknown artist"))

    def test_registry_rejects_unregistered_service(self):
        with self.assertRaisesRegex(PublicAPIError, "Available services: music, weather"):
            call_public_api("movies", "some query")


if __name__ == "__main__":
    unittest.main()

from backend import test
from backend.util.movie_fetcher import fetch_movie_details


class TestMovieFetcher(test.TestCase):
    def test_fetch_movie_details(self):
        # TODO: In an "real" unit-test we wouldn't want to fetch from an external API
        movie = fetch_movie_details("2001: A Space Odyssey")
        self.assertEqual("tt0062622", movie["imdbID"])

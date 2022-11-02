from backend import test
from backend.movie import Movie
from backend.util.movie_fetcher import fetch_movies


class TestUser(test.TestCase):
    def test_create(self):
        # TODO: In an "real" unit-test we wouldn't want to fetch from an external API
        # TODO: But then again, the tendency to over-rely on mocking has some serious drawbacks as well
        movies = fetch_movies("dude", from_page=1, to_page=5, max_amount=15)
        for movie in movies:
            Movie.create(movie)

        self.assertEqual(15, len(movies))
        self.assertEqual("Dude, Where's My Car?", Movie.get_by_imdb_id("tt0242423").title)

    def test_get_page(self):
        # TODO: Why doesn't this work in setUp?
        movies = fetch_movies("dude", from_page=1, to_page=5, max_amount=15)
        for movie in movies:
            Movie.create(movie)

        results = Movie.get_page(limit=5)
        self.assertEqual(5, len(results))
        self.assertEqual("Dude", results[0].title)
        self.assertEqual("Dude", results[1].title)
        self.assertEqual("Dude Bro Party Massacre III", results[2].title)
        self.assertEqual("Dude, What Would Happen", results[4].title)

        results = Movie.get_page(limit=5, offset=2)
        self.assertEqual(5, len(results))
        self.assertEqual("Dude Bro Party Massacre III", results[0].title)
        self.assertEqual("Dude Duck", results[1].title)
        self.assertEqual("Dude, What Would Happen", results[2].title)
        self.assertEqual("Dude, Where's My Car?", results[3].title)
        self.assertEqual("Dude, Where's My Cat?", results[4].title)

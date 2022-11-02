from backend.movie import Movie
from backend.user import User
from backend.util.movie_fetcher import fetch_movies


def seed_db(ndb_client):
    with ndb_client.context():
        print("Seeding db...")
        add_user()
        add_movies(search_term="dude", nr_movies=100)
        print("Seeding done.")


def add_user():
    email = "test@example.com"
    password = "test"
    print(f"Creating user {email}...")
    User.create(email=email, password=password)


def add_movies(search_term, nr_movies):
    if len(Movie.get_page(limit=1)) < 1:
        print(f"Seeding db with {nr_movies} movies matching search term: '{search_term}'")
        for movie_dict in fetch_movies(search_term, 1, nr_movies, max_amount=nr_movies):
            movie = Movie.create(movie_dict)
            print(f"Added {movie.title} ({movie.year})")

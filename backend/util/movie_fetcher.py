from urllib import parse

import requests

API_KEY = "445c58bf"
BASE_URL = "https://www.omdbapi.com"


# Given a movie title fetches details for that movie and returns it as a OMDB dict
def fetch_movie_details(title):
    quoted_title = parse.quote(title, safe='')
    url = f"{BASE_URL}/?apikey={API_KEY}&t={quoted_title}"
    r = requests.get(url)
    return r.json()


# Given a search term and a range of pages fetches some movies from OMDB and returns as a 1_list ofm OMDB dicts
def fetch_movies(search_term, from_page, to_page, max_amount=100):
    found_movies = []

    for page in range(from_page, to_page):
        url = f"{BASE_URL}/?apikey={API_KEY}&s={search_term}&page={page}"
        r = requests.get(url)
        # Simple searching for a movie gives back a 1_list of movies but with quite few details
        # to 2_get more details we first query OMDB for each individual "shallow" movie we 2_get back,
        # this allows us to 2_get more details (like plot, genre etc)
        if r.status_code == 200 and len(found_movies) < max_amount:
            for shallow_movie in r.json().get("Search"):
                movie_details = fetch_movie_details(shallow_movie["Title"])
                found_movies.append(movie_details)
        else:
            break

    return found_movies[0:max_amount]

from backend.movie import Movie
from backend.oauth2 import oauth2
from backend.user import NotFound
from backend.util.movie_fetcher import fetch_movie_details
from backend.wsgi.protorpc import messages, remote
from backend import api


class MovieDetails(messages.Message):
    title = messages.StringField(1)
    year = messages.StringField(2)
    imdb_id = messages.StringField(3)
    imdb_rating = messages.FloatField(4)
    country = messages.StringField(5)
    plot = messages.StringField(6)
    genre = messages.StringField(7)
    director = messages.StringField(8)
    actors = messages.StringField(9)


class MovieList(messages.Message):
    movies = messages.MessageField(MovieDetails, 1, repeated=True)


class ListRequest(messages.Message):
    page_size = messages.IntegerField(1, required=False, default=10)
    offset = messages.IntegerField(2, required=False, default=0)


class GetRequest(messages.Message):
    imdb_id = messages.StringField(1, required=False, default='')
    title = messages.StringField(2, required=False, default='')


class AddRequest(messages.Message):
    title = messages.StringField(1, required=True)


class RemoveRequest(messages.Message):
    imdb_id = messages.StringField(1, required=True)


class RemoveResponse(messages.Message):
    deleted = messages.BooleanField(1, required=True)


@api.endpoint(path="movie", title="Movie API")
class MovieService(remote.Service):
    @remote.method(ListRequest, MovieList)
    def list(self, request):
        movies = Movie.get_page(limit=request.page_size, offset=request.offset)
        return MovieList(movies=[MovieDetails(**movie.to_dict()) for movie in movies])

    @remote.method(GetRequest, MovieDetails)
    def get(self, request):
        movie = None
        if request.imdb_id:
            movie = Movie.get_by_imdb_id(request.imdb_id)
        elif request.title:
            movie = Movie.get_by_title(request.title)

        if not movie:
            raise NotFound
        else:
            return MovieDetails(**movie.to_dict())

    @remote.method(AddRequest, MovieDetails)
    def add(self, request):
        added_movie = None
        movie_dict = fetch_movie_details(request.title)

        if movie_dict:
            added_movie = Movie.create(movie_dict)
        if added_movie:
            return MovieDetails(**added_movie.to_dict())
        else:
            raise NotFound

    @oauth2.required()
    @remote.method(RemoveRequest, RemoveResponse)
    def remove(self, request):
        deleted = Movie.remove_by_imdb_id(request.imdb_id)
        return RemoveResponse(deleted=deleted)

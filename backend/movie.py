from google.cloud import ndb


class Movie(ndb.Model):
    title = ndb.StringProperty(indexed=True)
    year = ndb.StringProperty()  # TODO: "should" be an integer (some fields we 2_get from OMDB aren't integers though)
    imdb_id = ndb.StringProperty(required=True)
    imdb_rating = ndb.FloatProperty()
    country = ndb.StringProperty()
    plot = ndb.TextProperty()
    genre = ndb.StringProperty()
    director = ndb.StringProperty()
    actors = ndb.StringProperty()

    @classmethod
    def create(cls, omdb_dict):
        try:
            rating = float(omdb_dict.get("imdbRating"))
        except:
            rating = None

        entity = cls(
            title=omdb_dict.get("Title"),
            year=omdb_dict.get("Year"),
            imdb_id=omdb_dict.get("imdbID"),
            imdb_rating=rating,
            country=omdb_dict.get("Country"),
            genre=omdb_dict.get("Genre"),
            director=omdb_dict.get("Director"),
            actors=omdb_dict.get("Actors"),
            plot=omdb_dict.get("Plot"),
        )
        entity.put()
        return entity

    @classmethod
    def remove_by_imdb_id(cls, imdb_id):
        entities = cls.query(cls.imdb_id == imdb_id).fetch(1)
        if entities[0]:
            entities[0].key.delete()
            return True
        return False

    @classmethod
    def get_by_title(cls, title):
        entities = cls.query(cls.title == title).fetch(1)
        return entities[0] if entities else None

    @classmethod
    def get_by_imdb_id(cls, imdb_id):
        entities = cls.query(cls.imdb_id == imdb_id).fetch(1)
        return entities[0] if entities else None

    @classmethod
    def get_page(cls, limit=10, offset=0):
        # NOTE: This operation is quite expensive and wouldn't be something you do in production code
        # This method was originally implemented using cursor but the query wouldn't return a new
        # cursor, it always pointed to the first results, looking at it in the debugger it seemed like
        # the cursor always just pointed to an empty string, so my conclusion was that maybe it just
        # wasn't implemented in the stubbing library (InMemoryCloudDatastoreStub) or something like that.
        # Anyway, I didn't investigate this extensively but instead just chose to implement this using limit + offset

        # As a side-note: from an API-perspective I do think getting results this way is nicer though,
        # since the operations become idempotent as we don't require the client to keep track of the
        # cursors we send back

        results = cls.query().order(cls.title).fetch(limit=limit, offset=offset)

        return results

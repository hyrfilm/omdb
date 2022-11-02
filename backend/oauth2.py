"""
Oauth2 implementation using Resource Owner Password Credentials:
https://tools.ietf.org/html/draft-ietf-oauth-v2-30#section-1.3.3
"""
import datetime
import random
import functools

from google.cloud import ndb

from backend import user, error


class Unauthorized(error.Error):
    pass


class Decorator(object):
    """
    Protorpc method decorators. Reads the Authorization header, or authorization
    query paramater, and exposes self.session.
    """
    def __call__(self, *args, **kwargs):
        return self.required()(*args, **kwargs)

    @classmethod
    def required(cls):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                authorization = self.request_state.headers.get("AUTHORIZATION", "")

                self.session = Oauth2.get(authorization.replace("Bearer ", ""))

                return func(self, *args, **kwargs)

            wrapper.oauth2_required = True
            return wrapper
        return decorator

    @classmethod
    def optional(cls):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                self.session = None

                authorization = self.request_state.headers.get("AUTHORIZATION", "")

                try:
                    self.session = Oauth2.get(authorization.replace("Bearer ", ""))
                except Unauthorized:
                    pass

                return func(self, *args, **kwargs)

            wrapper.oauth2_optional = True
            return wrapper
        return decorator


oauth2 = Decorator


class Oauth2(ndb.Model):
    created = ndb.DateTimeProperty(indexed=False)
    user_key = ndb.KeyProperty(indexed=False)
    access_token_token = ndb.StringProperty(indexed=True)
    refresh_token_token = ndb.StringProperty(indexed=True)

    def __init__(self, *args, **kwargs):
        super(Oauth2, self).__init__(*args, **kwargs)
        self._access_token = None
        self._refresh_token = None

    @property
    def access_token(self):
        if self._access_token is None:
            self._access_token = AccessToken(self.access_token_token, self.created)
        return self._access_token

    @property
    def refresh_token(self):
        if self._refresh_token is None:
            self._refresh_token = RefreshToken(self.refresh_token_token, self.created)
        return self._refresh_token

    @property
    def user(self):
        return user.User.get(self.user_key.urlsafe())

    @classmethod
    def create(cls, user_key, access_token=None, refresh_token=None):
        if access_token is None:
            access_token = AccessToken.create()
        if refresh_token is None:
            refresh_token = RefreshToken.create()

        entity = cls.get_or_insert(ndb.Key(cls, access_token.token).id())
        if entity.user_key is not None and not entity.refresh_token.expired():
            raise Exception("Token collision: %s" % access_token.token)

        entity._access_token = None
        entity._refresh_token = None

        entity.update(
            created=datetime.datetime.now(),
            user_key=user_key,
            access_token_token=access_token.token,
            refresh_token_token=refresh_token.token
        )

        return entity

    @classmethod
    def _get(cls, token):
        return ndb.Key(cls, token).get()

    @classmethod
    def get(cls, token):
        if token:
            entity = cls._get(token)

            if entity is not None:
                if not entity.access_token.expired():
                    return entity

        raise Unauthorized("Invalid or expired access token")

    @classmethod
    def renew(cls, token, refresh_token):
        if token:
            entity = cls._get(token)

            if entity is not None:
                if entity.refresh_token.token != refresh_token or entity.refresh_token.expired():
                    raise Unauthorized("Invalid or expired refresh token")
                entity.revoke()
                return cls.create(entity.user_key)

        raise Unauthorized("Invalid or expired access token")

    def update(self, **kwargs):
        updates = [setattr(self, key, value) for key, value in kwargs.items() if getattr(self, key) != value]
        if len(updates) > 0:
            self.put()
        return self

    def expire(self):
        t = datetime.datetime.now() - datetime.timedelta(seconds=1)
        self.access_token.expires = t
        self.refresh_token.expires = t
        self.put()

    def revoke(self):
        t = datetime.datetime.now() - datetime.timedelta(days=1)
        self.access_token.expires = t
        self.refresh_token.expires = t
        self.put()


class AccessToken(object):
    def __init__(self, token, created=None):
        self.token = token
        self.expires = (created or datetime.datetime.now()) + datetime.timedelta(hours=6)

    @classmethod
    def create(cls):
        return cls("%040x" % random.getrandbits(160))

    def expired(self):
        return datetime.datetime.now() > self.expires


class RefreshToken(object):
    def __init__(self, token, created=None):
        self.token = token
        self.expires = (created or datetime.datetime.now()) + datetime.timedelta(days=10)

    @classmethod
    def create(cls):
        return cls("%040x" % random.getrandbits(160))

    def expired(self):
        return datetime.datetime.now() > self.expires

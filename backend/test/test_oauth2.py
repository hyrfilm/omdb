import datetime

from backend import api, wsgi, test, oauth2
from backend.wsgi import messages, message_types

from google.cloud import ndb


class TestResponse(messages.Message):
    id = messages.StringField(1, required=True)


@api.service("test")
class Oauth2(wsgi.Service):
    @oauth2.oauth2.required()
    @wsgi.method(message_types.VoidMessage, TestResponse)
    def required(self, request):
        return TestResponse(id=self.session.user_key.id())

    @oauth2.oauth2()
    @wsgi.method(message_types.VoidMessage, TestResponse)
    def required_shorthand(self, request):
        return TestResponse(id=self.session.user_key.id())

    @oauth2.oauth2.optional()
    @wsgi.method(message_types.VoidMessage, TestResponse)
    def optional(self, request):
        return TestResponse(id=self.session.user_key.id() if self.session else "none")


class TestOauth2(test.TestCase):

    def test_create(self):
        session = oauth2.Oauth2.create(ndb.Key("Test", "123"))
        session = oauth2.Oauth2.get(session.access_token.token)
        self.assertRaises(oauth2.Unauthorized, lambda: oauth2.Oauth2.get(None))
        self.assertRaises(oauth2.Unauthorized, lambda: oauth2.Oauth2.get(""))
        self.assertTrue(session.access_token.token)
        self.assertTrue(session.refresh_token.token)
        self.assertTrue(session.access_token.expires > datetime.datetime.now())
        self.assertTrue(session.refresh_token.expires > session.access_token.expires)
        self.assertEqual(session.user_key, ndb.Key("Test", "123"))
        session.revoke()
        self.assertTrue(session.access_token.expired())
        self.assertTrue(session.refresh_token.expired())

    def test_expire(self):
        session = oauth2.Oauth2.create(ndb.Key("Test", "123"))
        session.access_token.expires = datetime.datetime.now() - datetime.timedelta(seconds=1)
        self.assertTrue(session.access_token.expired())

    def test_renew(self):
        session = oauth2.Oauth2.create(ndb.Key("Test", "123"))

        self.assertRaises(oauth2.Unauthorized, lambda: oauth2.Oauth2.renew(session.access_token.token, "this_should_fail"))

        new_session = oauth2.Oauth2.renew(session.access_token.token, session.refresh_token.token)

        self.assertEqual(session.user_key, new_session.user_key)
        self.assertTrue(session.access_token.token != new_session.access_token.token)

    def test_collision(self):
        access_token = oauth2.AccessToken("token")
        oauth2.Oauth2.create(ndb.Key("Test", "12345"), access_token=access_token)
        self.assertRaises(Exception, lambda: oauth2.Oauth2.create(ndb.Key("Test", "12345"), access_token=access_token))

    def test_reuse(self):
        access_token = oauth2.AccessToken("token")
        session = oauth2.Oauth2.create(ndb.Key("Test", "123"), access_token=access_token)
        session.update(created=datetime.datetime.now() - datetime.timedelta(days=30))
        # reuse
        access_token = oauth2.AccessToken("token")
        session = oauth2.Oauth2.create(ndb.Key("Test", "123"), access_token=access_token)
        self.assertTrue(session.access_token.expires > datetime.datetime.now())
        self.assertTrue(session.refresh_token.expires > datetime.datetime.now())


class TestOauth2Api(test.TestCase):
    def test_authorized(self):
        session = oauth2.Oauth2.create(ndb.Key("Test", "123"))
        access_token = session.access_token.token

        # required
        resp = self.api_client.post("test.required_shorthand", headers=dict(authorization=access_token))
        self.assertEqual(resp.get("error"), None)

        resp = self.api_client.post("test.required", headers=dict(authorization=access_token))
        self.assertEqual(resp.get("error"), None)

        resp = self.api_client.post("test.required", headers=dict(authorization=access_token))
        self.assertEqual(resp.get("error"), None)

        resp = self.api_client.post("test.required", headers=dict(authorization=access_token))
        self.assertEqual(resp.get("error"), None)

        # optional
        resp = self.api_client.post("test.optional", headers=dict(authorization=access_token))
        self.assertEqual(resp.get("error"), None)

        resp = self.api_client.post("test.optional", headers=dict(authorization=access_token))
        self.assertEqual(resp.get("error"), None)

    def test_unauthorized(self):
        # required
        resp = self.api_client.post("test.required_shorthand")
        error = resp.get("error")
        self.assertEqual(error.get("error_name"), "Unauthorized")

        resp = self.api_client.post("test.required")
        error = resp.get("error")
        self.assertEqual(error.get("error_name"), "Unauthorized")

        resp = self.api_client.post("test.required", headers=dict(authorization="this_token_is_invalid"))
        error = resp.get("error")
        self.assertEqual(error.get("error_name"), "Unauthorized")

        resp = self.api_client.post("test.required", headers=dict(authorization=""))
        error = resp.get("error")
        self.assertEqual(error.get("error_name"), "Unauthorized")

    def test_expire(self):
        session = oauth2.Oauth2.create(ndb.Key("Test", "123"))
        session.expire()

        resp = self.api_client.post("test.required", headers=dict(authorization=session.access_token.token))
        error = resp.get("error")
        self.assertTrue(error)
        self.assertEqual(error.get("error_name"), "Unauthorized")

    def test_revoke(self):
        session = oauth2.Oauth2.create(ndb.Key("Test", "123"))
        session.revoke()

        resp = self.api_client.post("test.required", headers=dict(authorization=session.access_token.token))
        error = resp.get("error")
        self.assertTrue(error)
        self.assertEqual(error.get("error_name"), "Unauthorized")

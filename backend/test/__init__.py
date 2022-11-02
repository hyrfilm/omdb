import unittest

# activate stubs
import backend.stub.logging  # noqa F401
import backend.stub.ndb  # noqa F401
#

from google.cloud import ndb

from backend import api


class TestCase(unittest.TestCase):
    def setUp(self):
        # set up ndb context
        self.ndb_context = ndb.Client().context()
        self.ndb_context.__enter__()

        # set up api client
        self.api_client = api.application.client

    def tearDown(self):
        # tear down ndb context
        self.ndb_context.__exit__(None, None, None)

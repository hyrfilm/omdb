from google.cloud import ndb

from InMemoryCloudDatastoreStub import datastore_stub


class Client:
    def __init__(self, project=None, namespace=None, credentials=None):
        self.project = project or "stub"
        self.namespace = namespace
        self.credentials = credentials
        self.stub = datastore_stub.LocalDatastoreStub()
        self._context = ndb.context.Context(self)

    def context(self):
        return self._context.use()


ndb.Client = Client

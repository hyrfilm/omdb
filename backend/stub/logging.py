from google.cloud import logging
from google.cloud.logging.logger import Logger


class Client:
    def __init__(self, project=None, namespace=None, credentials=None):
        self.project = project or "stub"
        self.namespace = namespace
        self.credentials = credentials

    def logger(self, name):
        return Logger(name, client=self)


logging.Client = Client

import logging
import os

from backend.util.db import seed_db

if not os.getenv('GAE_APPLICATION'):
    # if we are running locally, activate stubs for local
    import backend.stub.logging  # noqa F401
    import backend.stub.ndb  # noqa F401
    #

from google.cloud import ndb

from backend.api import application as api_application
from backend.gunicorn.log_handler import LogHandler

ndb_client = ndb.Client()

log_handler = LogHandler()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
seed_db(ndb_client)


def application(environ, start_response):
    log_handler.trace_context = environ.get('HTTP_X_CLOUD_TRACE_CONTEXT')

    with ndb_client.context():
        response = api_application(environ, start_response)

        return [r.encode("utf-8") if isinstance(r, str) else r for r in response]  # gunicorn expects bytes

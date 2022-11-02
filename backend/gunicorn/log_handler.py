from google.cloud.logging import Client
from google.cloud.logging.handlers import AppEngineHandler


class LogHandler(AppEngineHandler):
    def __init__(self, trace_context=None):
        super().__init__(
            client=Client(),
            name="appengine.googleapis.com%2Fstdout"
        )
        self.trace_context = trace_context

    @property
    def trace_id(self):
        return self.trace_context.split('/')[0] if self.trace_context else None

    def get_gae_labels(self):
        return {
            "appengine.googleapis.com/trace_id": self.trace_id
        } if self.trace_id else {}

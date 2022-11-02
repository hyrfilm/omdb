import json

from .protorpc import remote, messages, message_types  # noqa F401
from .protorpc.wsgi import service

from urllib import parse as urlparse
from io import StringIO, BytesIO


class Client:
    def __init__(self, application):
        self.application = application
        self.status = ''

    def _start_response(self, status, _):
        self.status = status

    def _request(self, url, method='POST', data=None, headers=dict()):
        url = urlparse.urlparse(url)
        path_info = url.path

        if not path_info.startswith("/%s/" % self.application.base_path):
            path_info = "/%s/%s" % (self.application.base_path, path_info)

        env = dict(
            QUERY_STRING=url.query,
            REQUEST_METHOD=method,
            PATH_INFO=path_info
        )

        for k, v in headers.items():
            env.update({'%s' % k.replace('-', '_').upper(): '%s' % v})
            env.update({'HTTP_%s' % k.replace('-', '_').upper(): '%s' % v})

        if method == 'POST':
            if isinstance(data, bytes):
                env['wsgi.input'] = BytesIO(data)
                env.update(dict(
                    CONTENT_TYPE="application/octet-stream",
                    CONTENT_LENGTH="%s" % len(data)
                ))
            else:
                json_data = json.dumps(data or dict())
                env['wsgi.input'] = StringIO(json_data)
                env.update(dict(
                    CONTENT_TYPE="application/json",
                    CONTENT_LENGTH="%s" % len(json_data)
                ))

        resp = self.application(env, self._start_response)[0]

        try:
            body = json.loads(resp)
        except ValueError:
            body = dict(
                error_message=resp.strip()
            )
        if self.status != '200 OK':
            body = dict(
                error=dict(
                    code=self.status,
                    error_name=body.get("error_name"),
                    message=body.get("error_message")
                )
            )
        return body

    def post(self, url, data=None, headers=dict()):
        return self._request(url, method="POST", data=data, headers=headers)

    def get(self, url, headers=dict()):
        return self._request(url, method="GET", headers=headers)


class Application:
    def __init__(self, base_path):
        self.base_path = base_path
        self.services = []
        self._app = None
        self._client = None

    @property
    def app(self):
        if self._app is None:
            self._app = service.service_mappings([(s.path, s) for s in self.services], registry_path=None)
        return self._app

    @property
    def client(self):
        if self._client is None:
            self._client = Client(self)
        return self._client

    def __call__(self, environ, start_response):
        if environ.get('REQUEST_METHOD') in ["OPTIONS"]:
            start_response('200 OK', [
                ('Access-Control-Allow-Headers', 'authorization, origin, content-type, accept'),
                ('Access-Control-Max-Age', '600'),
                ('Access-Control-Allow-Origin', '*')
            ])
            return ['']

        if environ.get('REQUEST_METHOD') in ["GET", "POST"]:
            if environ.get('REQUEST_METHOD') in ["GET"]:
                content = json.dumps(dict(urlparse.parse_qsl(environ.get('QUERY_STRING'))))
                environ['wsgi.input'] = StringIO(content)
                environ['CONTENT_LENGTH'] = len(content)

            environ['REQUEST_METHOD'] = 'POST'

            if environ.get('CONTENT_TYPE') not in ['application/octet-stream']:
                environ['CONTENT_TYPE'] = 'application/json'

            return self.app(
                environ,
                lambda status, headers: start_response(status, headers + [('Access-Control-Allow-Origin', '*')])
            )

        start_response('405 Method Not Allowed', [('Allow', 'OPTIONS, GET, POST')])
        return ['']

    def service(self, path, title=""):
        def decorator(f):
            f.title = title
            f.path = "/%s/%s" % (self.base_path, path)
            if f.path not in [s.path for s in self.services]:
                self.services.append(f)
            return f
        return decorator


Service = remote.Service
ApplicationError = remote.ApplicationError
method = remote.method

from backend.wsgi import ApplicationError


class Error(ApplicationError):
    def __init__(self, message=None):
        super(Error, self).__init__(message, error_name=self.__class__.__name__)

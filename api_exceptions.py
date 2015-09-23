class APIException(Exception):
    status_code = 400

    def __init__(self, message='no message given', status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class NoDataException(APIException):
    pass


class NoTableException(APIException):
    pass


class FilterParsingException(APIException):
    pass


class BadFilterException(APIException):
    pass


class BadRequestException(APIException):
    pass


class LivestatusSocketException(APIException):
    pass


class InternalProcessingException(APIException):
    pass

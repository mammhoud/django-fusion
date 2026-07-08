from ninja_extra import status
from ninja_extra.exceptions import APIException


class ModelNotFoundException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Model not found"
    default_code = "bad_request"


class ApplicationError(Exception):
    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}

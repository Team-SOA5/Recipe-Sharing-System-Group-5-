from enum import Enum
from http import HTTPStatus


class ErrorCode(Enum):
    """
    Error codes for application exceptions
    Equivalent to ErrorCode.java enum
    """
    USER_NOT_EXISTED = (1001, "user not existed", HTTPStatus.NOT_FOUND)
    UNAUTHENTICATED = (1002, "unauthenticated - you are not allowed!", HTTPStatus.UNAUTHORIZED)
    UNAUTHORIZED = (1003, "unauthorized - you are not allowed!", HTTPStatus.FORBIDDEN)
    UNCATEGORIZED = (1004, "uncategorized exception", HTTPStatus.BAD_REQUEST)
    USER_EXISTED = (1005, "user existed", HTTPStatus.BAD_REQUEST)
    UNABLE_ACCOUNT = (1006, "account was unable!", HTTPStatus.BAD_REQUEST)
    CAN_NOT_CREATE_TOKEN = (1007, "cannot create token", HTTPStatus.BAD_REQUEST)
    ROLE_NOT_EXISTED = (1008, "role not existed", HTTPStatus.NOT_FOUND)
    FILE_NOT_EXISTED = (1009, "file not existed", HTTPStatus.NOT_FOUND)
    
    def __init__(self, code: int, message: str, http_status: HTTPStatus):
        self.code = code
        self.message = message
        self.http_status = http_status


class AppException(Exception):
    """
    Custom application exception
    Equivalent to AppException.java
    """
    
    def __init__(self, error_code: ErrorCode):
        self.error_code = error_code
        super().__init__(error_code.message)
    
    def get_error_code(self) -> ErrorCode:
        return self.error_code

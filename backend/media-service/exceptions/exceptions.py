from enum import Enum


class ErrorCode(Enum):
    """
    Enum cho error codes - tương ứng với ErrorCode trong Java
    """
    USER_NOT_EXISTED = (1001, "user not existed", 404)
    UNAUTHENTICATED = (1002, "unauthenticated - you are not allowed!", 401)
    UNAUTHORIZED = (1003, "unauthorized - you are not allowed!", 403)
    UNCATEGORIZED = (1004, "uncategorized exception", 400)
    USER_EXISTED = (1005, "user existed", 400)
    UNABLE_ACCOUNT = (1006, "account was unable!", 400)
    CAN_NOT_CREATE_TOKEN = (1007, "cannot create token", 400)
    ROLE_NOT_EXISTED = (1008, "role not existed", 404)
    FILE_NOT_EXISTED = (1009, "file not existed", 404)
    
    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status


class AppException(Exception):
    """
    Custom application exception - tương ứng với AppException trong Java
    """
    def __init__(self, error_code: ErrorCode):
        self.error_code = error_code
        super().__init__(error_code.message)

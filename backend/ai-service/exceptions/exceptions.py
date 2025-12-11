from enum import Enum
from http import HTTPStatus

class ErrorCode(Enum):
    # Định dạng: (custom_code, message, http_status_enum)
    SUCCESS = (0, "Success", HTTPStatus.OK)
    UNKNOWN_ERROR = (1000, "Unknown error", HTTPStatus.INTERNAL_SERVER_ERROR)
    INVALID_REQUEST = (1001, "Invalid request", HTTPStatus.BAD_REQUEST)
    UNAUTHENTICATED = (1002, "Vui lòng đăng nhập để tiếp tục", HTTPStatus.UNAUTHORIZED)
    FORBIDDEN = (1003, "Bạn không có quyền thực hiện thao tác này", HTTPStatus.FORBIDDEN)
    NOT_FOUND = (1004, "Không tìm thấy tài nguyên", HTTPStatus.NOT_FOUND)
    
    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status

# Các Custom Exception class dùng trong Controller
class AppError(Exception):
    def __init__(self, error_code: ErrorCode, message=None):
        self.error_code = error_code
        self.message = message or error_code.message
        super().__init__(self.message)

class NotFoundError(AppError):
    def __init__(self, message=None):
        super().__init__(ErrorCode.NOT_FOUND, message)

class ValidationError(AppError):
    def __init__(self, message=None):
        super().__init__(ErrorCode.INVALID_REQUEST, message)

class UnauthorizedError(AppError):
    def __init__(self, message=None):
        super().__init__(ErrorCode.UNAUTHENTICATED, message)
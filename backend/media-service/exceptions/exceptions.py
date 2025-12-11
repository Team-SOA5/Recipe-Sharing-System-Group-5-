from enum import Enum
from http import HTTPStatus

class ErrorCode(Enum):
    # Định nghĩa các mã lỗi
    SUCCESS = (0, "Success", HTTPStatus.OK)
    UNKNOWN_ERROR = (1000, "Unknown error", HTTPStatus.INTERNAL_SERVER_ERROR)
    INVALID_REQUEST = (1001, "Invalid request", HTTPStatus.BAD_REQUEST)
    UNAUTHENTICATED = (1002, "Unauthenticated", HTTPStatus.UNAUTHORIZED)
    FORBIDDEN = (1003, "Forbidden", HTTPStatus.FORBIDDEN)
    NOT_FOUND = (1004, "Not found", HTTPStatus.NOT_FOUND)
    
    # Các lỗi liên quan đến File (Media Service)
    NO_FILE_UPLOADED = (1011, "No file uploaded", HTTPStatus.BAD_REQUEST)
    FILE_SAVE_ERROR = (1010, "Cannot save file", HTTPStatus.INTERNAL_SERVER_ERROR)
    FILE_NOT_FOUND = (1009, "File not existed", HTTPStatus.NOT_FOUND)

    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status

# Class Exception tùy chỉnh mà Repository đang gọi
class AppError(Exception):
    def __init__(self, error_code: ErrorCode, message=None):
        self.error_code = error_code
        self.message = message or error_code.message
        super().__init__(self.message)
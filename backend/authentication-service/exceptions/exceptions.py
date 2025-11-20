from enum import Enum
from http import HTTPStatus


class ErrorCode(Enum):
    """Error codes - equivalent to Java ErrorCode enum"""
    
    USER_NOT_EXISTED = (1001, "Người dùng không tồn tại", HTTPStatus.NOT_FOUND)
    UNAUTHENTICATED = (1002, "Vui lòng đăng nhập để tiếp tục", HTTPStatus.UNAUTHORIZED)
    UNAUTHORIZED = (1003, "unauthorized - you are not allowed!", HTTPStatus.FORBIDDEN)
    UNCATEGORIZED = (1004, "uncategorized exception", HTTPStatus.BAD_REQUEST)
    USER_EXISTED = (1005, "Người dùng đã tồn tại", HTTPStatus.BAD_REQUEST)
    CAN_NOT_CREATE_TOKEN = (1007, "cannot create token", HTTPStatus.BAD_REQUEST)
    ROLE_NOT_EXISTED = (1008, "role not existed", HTTPStatus.NOT_FOUND)
    FAIL_REGISTRATION = (1009, "Đăng ký thất bại!", HTTPStatus.NOT_FOUND)
    INVALID_PASSWORD = (1010, "Mật khẩu phải có ít nhất 8 ký tự", HTTPStatus.BAD_REQUEST)
    INVALID_EMAIL = (1011, "Địa chỉ email không hợp lệ", HTTPStatus.BAD_REQUEST)
    EMAIL_IS_REQUIRED = (1012, "Điền email", HTTPStatus.BAD_REQUEST)
    INVALID_KEY = (1013, "invalid key error", HTTPStatus.BAD_REQUEST)
    INVALID_USERNAME = (1014, "username phải có ít nhất 5 ký tự", HTTPStatus.BAD_REQUEST)
    USERNAME_EXISTED = (1015, "username đã tồn tại", HTTPStatus.BAD_REQUEST)
    
    def __init__(self, code: int, message: str, http_status: HTTPStatus):
        self.code = code
        self.message = message
        self.http_status = http_status


class AppException(Exception):
    """Application exception - equivalent to Java AppException"""
    
    def __init__(self, error_code: ErrorCode):
        self.error_code = error_code
        super().__init__(error_code.message)

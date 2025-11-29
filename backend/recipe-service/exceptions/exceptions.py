from enum import Enum

class HttpStatus(Enum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

class ErrorCode(Enum):
    # Auth Errors (Khớp với jwt_service.py)
    UNAUTHENTICATED = (1002, "Vui lòng đăng nhập để tiếp tục", HttpStatus.UNAUTHORIZED)
    UNAUTHORIZED = (1003, "Bạn không có quyền thực hiện thao tác này", HttpStatus.FORBIDDEN)
    
    # Recipe Errors
    RECIPE_NOT_FOUND = (2001, "Không tìm thấy công thức", HttpStatus.NOT_FOUND)
    MISSING_FIELDS = (2003, "Thiếu thông tin bắt buộc", HttpStatus.BAD_REQUEST)
    INTERNAL_ERROR = (5000, "Lỗi hệ thống", HttpStatus.INTERNAL_SERVER_ERROR)
    
    def __init__(self, code, message, http_status):
        self.code = code
        self.message = message
        self.http_status = http_status
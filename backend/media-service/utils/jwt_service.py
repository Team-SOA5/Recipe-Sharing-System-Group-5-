import jwt
import os
from functools import wraps
from flask import request, g
from config import app_config
from exceptions.exceptions import AppError, ErrorCode

def jwt_required(f):
    """
    Decorator để kiểm tra JWT token.
    Có tính năng SKIP_AUTH để test nhanh mà không cần token.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # --- [NEW] LOGIC BỎ QUA AUTH ---
        # Kiểm tra biến môi trường SKIP_AUTH (mặc định là false)
        skip_auth = os.getenv('SKIP_AUTH', 'false').lower() == 'true'
        
        if skip_auth:
            # Gán thông tin giả lập để code phía sau không bị crash
            g.user_id = "dev_user_123"
            g.user_role = "ADMIN"
            # Cho qua luôn, không check token nữa
            return f(*args, **kwargs)
        
        # --- LOGIC CHÍNH (NHƯ CŨ) ---
        token = None
        
        # 1. Lấy token từ Header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        # 2. Kiểm tra nếu không có token
        if not token:
            raise AppError(ErrorCode.UNAUTHORIZED, "Authentication token is missing")

        try:
            # 3. Decode token
            payload = jwt.decode(
                token, 
                app_config.config.get('SECRET_KEY', 'my_precious_secret_key'), 
                algorithms=["HS256"]
            )
            
            # 4. Lưu thông tin user vào biến global g
            g.user_id = payload.get('sub') or payload.get('id')
            g.user_role = payload.get('role')
            
        except jwt.ExpiredSignatureError:
            raise AppError(ErrorCode.UNAUTHORIZED, "Token has expired")
        except jwt.InvalidTokenError:
            raise AppError(ErrorCode.UNAUTHORIZED, "Invalid token")
        except Exception as e:
            raise AppError(ErrorCode.UNAUTHORIZED, f"Token error: {str(e)}")

        return f(*args, **kwargs)

    return decorated
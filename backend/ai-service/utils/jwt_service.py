import jwt
from functools import wraps
from flask import request, g, jsonify
from exceptions.exceptions import ErrorCode
import logging
import os

logger = logging.getLogger(__name__)

# [CẤU HÌNH] Bật/Tắt chế độ bỏ qua Auth
# Nên đặt trong file .env: SKIP_AUTH=True
SKIP_AUTH = os.getenv('SKIP_AUTH', 'False').lower() == 'true'
MOCK_USER_ID = "dev_user_id_123" # User ID giả lập để test

def decode_jwt(token):
    # ... (giữ nguyên logic cũ) ...
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        raise Exception("Invalid token")

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # [MỚI] Logic bỏ qua Auth nếu đang Dev
        if SKIP_AUTH:
            g.user_id = MOCK_USER_ID
            logger.warning(f"⚠️ SKIP AUTH MODE: Logged in as {g.user_id}")
            return f(*args, **kwargs)

        # --- Logic Auth bình thường (Production) ---
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            error_code = ErrorCode.UNAUTHENTICATED
            return jsonify({'code': error_code.code, 'message': error_code.message}), error_code.http_status.value
        
        try:
            decoded = decode_jwt(auth_header)
            g.user_id = decoded.get('sub')
            logger.info(f"Authenticated user: {g.user_id}")
        except Exception:
            error_code = ErrorCode.UNAUTHENTICATED
            return jsonify({'code': error_code.code, 'message': error_code.message}), error_code.http_status.value
        
        return f(*args, **kwargs)
    
    return decorated_function
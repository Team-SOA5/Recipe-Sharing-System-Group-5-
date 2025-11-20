import jwt
from functools import wraps
from flask import request, g
from datetime import datetime
from exceptions.exceptions import AppException, ErrorCode


class JwtService:
    """
    Service xử lý JWT token - tương ứng với CustomJwtDecoder trong Java
    """
    
    def __init__(self):
        # Trong Java, service này không verify signature vì chỉ parse token
        # Điều này tương tự như CustomJwtDecoder chỉ parse token mà không verify
        pass
    
    @staticmethod
    def decode_token(token):
        """
        Decode JWT token mà không verify signature
        Tương ứng với CustomJwtDecoder.decode() trong Java
        
        Args:
            token: JWT token string
            
        Returns:
            dict: Decoded claims từ token
            
        Raises:
            AppException: Nếu token invalid
        """
        try:
            # Decode token mà không verify signature (giống như Java implementation)
            # options={'verify_signature': False} tương ứng với việc chỉ parse SignedJWT
            decoded = jwt.decode(token, options={'verify_signature': False})
            
            # Kiểm tra expiration time
            if 'exp' in decoded:
                exp_timestamp = decoded['exp']
                if datetime.fromtimestamp(exp_timestamp) < datetime.now():
                    raise AppException(ErrorCode.UNAUTHENTICATED)
            
            return decoded
        except jwt.DecodeError:
            raise AppException(ErrorCode.UNAUTHENTICATED)
        except Exception:
            raise AppException(ErrorCode.UNAUTHENTICATED)
    
    @staticmethod
    def get_user_id_from_token(token):
        """
        Lấy user ID từ JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            str: User ID từ 'sub' claim
        """
        decoded = JwtService.decode_token(token)
        # Trong JWT, 'sub' (subject) thường chứa user ID
        return decoded.get('sub')


def token_required(f):
    """
    Decorator để bảo vệ endpoint, yêu cầu JWT token
    Tương ứng với SecurityConfig trong Java
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Lấy token từ Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            raise AppException(ErrorCode.UNAUTHENTICATED)
        
        try:
            # Decode token và lưu user_id vào g (Flask global context)
            user_id = JwtService.get_user_id_from_token(token)
            g.user_id = user_id
        except Exception:
            raise AppException(ErrorCode.UNAUTHENTICATED)
        
        return f(*args, **kwargs)
    
    return decorated_function

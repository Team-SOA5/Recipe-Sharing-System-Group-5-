import jwt
from functools import wraps
from flask import request, g, jsonify
from exceptions.exceptions import ErrorCode
import logging

logger = logging.getLogger(__name__)


def decode_jwt(token):
    """
    Decode JWT token without verification
    """
    try:
        # Remove "Bearer " prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decode without verification (like the Java implementation)
        # The Java code uses SignedJWT.parse() which doesn't verify signature
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        return decoded
    except jwt.DecodeError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise Exception("Invalid token")
    except Exception as e:
        logger.error(f"Error decoding token: {str(e)}")
        raise Exception("Invalid token")


def jwt_required(f):
    """
    Decorator for requiring JWT authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            error_code = ErrorCode.UNAUTHENTICATED
            return jsonify({
                'code': error_code.code,
                'message': error_code.message
            }), error_code.http_status.value
        
        try:
            # Decode token
            decoded = decode_jwt(auth_header)
            
            # Store user ID in Flask's g object (similar to SecurityContextHolder)
            # The Java code uses getName() which returns the subject claim
            g.user_id = decoded.get('sub')
            
            # Store decoded token for other uses
            g.token_claims = decoded
            
            logger.info(f"Authenticated user: {g.user_id}")
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            error_code = ErrorCode.UNAUTHENTICATED
            return jsonify({
                'code': error_code.code,
                'message': error_code.message
            }), error_code.http_status.value
        
        return f(*args, **kwargs)
    
    return decorated_function

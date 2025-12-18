import jwt
from datetime import datetime
from typing import Optional, Dict
from flask import current_app
from exceptions.exceptions import AppException, ErrorCode


def decode_jwt(token: str) -> Dict:
    """
    Decode and validate JWT token
    Equivalent to CustomJwtDecoder.decode() in Java
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary containing decoded JWT claims
        
    Raises:
        AppException: If token is invalid
    """
    try:
        # Parse the token without verification first to get header and claims
        unverified_header = jwt.get_unverified_header(token)
        unverified_claims = jwt.decode(token, options={"verify_signature": False})
        
        # Return a dictionary mimicking Spring Security's Jwt object structure
        decoded = {
            'token': token,
            'header': unverified_header,
            'claims': unverified_claims,
            'issuedAt': datetime.fromtimestamp(unverified_claims.get('iat', 0)),
            'expiresAt': datetime.fromtimestamp(unverified_claims.get('exp', 0))
        }
        
        return decoded
        
    except jwt.ExpiredSignatureError:
        raise AppException(ErrorCode.UNAUTHENTICATED)
    except jwt.InvalidTokenError:
        raise AppException(ErrorCode.UNAUTHENTICATED)
    except Exception as e:
        raise AppException(ErrorCode.UNAUTHENTICATED)


def verify_token(token: str, secret_key: Optional[str] = None, algorithm: str = 'HS256') -> bool:
    """
    Verify if a JWT token is valid
    
    Args:
        token: JWT token string
        secret_key: Secret key for verification (optional, uses app config if not provided)
        algorithm: Algorithm used for JWT (default: HS256)
        
    Returns:
        True if token is valid, False otherwise
    """
    try:
        if secret_key is None:
            secret_key = current_app.config.get('JWT_SECRET_KEY')
        
        jwt.decode(token, secret_key, algorithms=[algorithm])
        return True
    except:
        return False


def get_claim_from_token(token: str, claim_name: str) -> Optional[any]:
    """
    Extract a specific claim from JWT token
    
    Args:
        token: JWT token string
        claim_name: Name of the claim to extract
        
    Returns:
        Claim value or None if not found
    """
    try:
        decoded = decode_jwt(token)
        return decoded['claims'].get(claim_name)
    except:
        return None


def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from JWT token
    Common claim names: 'sub', 'userId', 'user_id'
    
    Args:
        token: JWT token string
        
    Returns:
        User ID or None if not found
    """
    user_id = get_claim_from_token(token, 'sub')
    if not user_id:
        user_id = get_claim_from_token(token, 'userId')
    if not user_id:
        user_id = get_claim_from_token(token, 'user_id')
    return user_id


def extract_username_from_token(token: str) -> Optional[str]:
    """
    Extract username from JWT token
    Common claim names: 'username', 'preferred_username', 'name'
    
    Args:
        token: JWT token string
        
    Returns:
        Username or None if not found
    """
    username = get_claim_from_token(token, 'username')
    if not username:
        username = get_claim_from_token(token, 'preferred_username')
    if not username:
        username = get_claim_from_token(token, 'name')
    return username


def extract_roles_from_token(token: str) -> list:
    """
    Extract roles/authorities from JWT token
    Common claim names: 'roles', 'authorities', 'scope'
    
    Args:
        token: JWT token string
        
    Returns:
        List of roles or empty list if not found
    """
    roles = get_claim_from_token(token, 'roles')
    if not roles:
        roles = get_claim_from_token(token, 'authorities')
    if not roles:
        scope = get_claim_from_token(token, 'scope')
        if scope:
            roles = scope.split(' ') if isinstance(scope, str) else scope
    
    return roles if roles else []

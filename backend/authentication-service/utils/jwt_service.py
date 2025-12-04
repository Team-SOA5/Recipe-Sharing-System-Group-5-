import jwt
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
from flask import current_app
from models.models import UserEntity
from exceptions.exceptions import AppException, ErrorCode
import logging

logger = logging.getLogger(__name__)


class JWTService:
    """JWT Service - handles token generation and verification"""
    
    @staticmethod
    def generate_access_token(user: UserEntity) -> str:
        """Generate access token for user"""
        try:
            payload = {
                'iss': current_app.config['JWT_ISSUER'],
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_DURATION']),
                'sub': user.id,
                'jti': str(uuid.uuid4()),
                'token-type': 'access',
                'scope': JWTService._build_scope(user)
            }
            
            token = jwt.encode(
                payload,
                current_app.config['JWT_SIGNER_KEY'],
                algorithm='HS512'
            )
            return token
        except Exception as e:
            logger.error(f"Error generating access token: {str(e)}")
            raise AppException(ErrorCode.CAN_NOT_CREATE_TOKEN)
    
    @staticmethod
    def generate_refresh_token(user: UserEntity) -> str:
        """Generate refresh token for user"""
        try:
            payload = {
                'iss': current_app.config['JWT_ISSUER'],
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_REFRESH_TOKEN_DURATION']),
                'sub': user.id,
                'jti': str(uuid.uuid4()),
                'token-type': 'refresh',
                'scope': JWTService._build_scope(user)
            }
            
            token = jwt.encode(
                payload,
                current_app.config['JWT_SIGNER_KEY'],
                algorithm='HS512'
            )
            return token
        except Exception as e:
            logger.error(f"Error generating refresh token: {str(e)}")
            raise AppException(ErrorCode.CAN_NOT_CREATE_TOKEN)
    
    @staticmethod
    def verify_token(token: str, is_refresh: bool = False) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        Returns the decoded payload if valid
        Raises AppException if invalid
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SIGNER_KEY'],
                algorithms=['HS512']
            )
            
            # Check token type
            token_type = payload.get('token-type')
            if is_refresh and token_type != 'refresh':
                raise AppException(ErrorCode.UNAUTHENTICATED)
            elif not is_refresh and token_type != 'access':
                raise AppException(ErrorCode.UNAUTHENTICATED)
            
            # Check expiration
            exp = payload.get('exp')
            if not exp or datetime.fromtimestamp(exp) <= datetime.utcnow():
                raise AppException(ErrorCode.UNAUTHENTICATED)
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.info("Token has expired")
            raise AppException(ErrorCode.UNAUTHENTICATED)
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise AppException(ErrorCode.UNAUTHENTICATED)
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            raise AppException(ErrorCode.UNAUTHENTICATED)
    
    @staticmethod
    def _build_scope(user: UserEntity) -> str:
        """Build scope string from user roles"""
        if user.role:
            roles = [f"ROLE_{role.name}" for role in user.role]
            return " ".join(roles)
        return ""

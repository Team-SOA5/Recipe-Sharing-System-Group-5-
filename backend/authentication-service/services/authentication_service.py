from extensions import bcrypt, db
from models.models import UserEntity, InvalidatedToken
from repositories.repositories import UserRepository, InvalidatedTokenRepository
from dto.requests import AuthenticationRequest, IntrospectRequest, LogoutRequest, RefreshTokenRequest
from dto.responses import AuthenticationResponse, IntrospectResponse, RefreshTokenResponse
from exceptions.exceptions import AppException, ErrorCode
from utils.jwt_service import JWTService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Authentication service"""
    
    @staticmethod
    def introspect(request: IntrospectRequest) -> IntrospectResponse:
        """
        Introspect access token to check if it's valid
        """
        valid = True
        try:
            payload = JWTService.verify_token(request.access_token, is_refresh=False)
            
            # Check if token is invalidated
            token_id = payload.get('jti')
            if InvalidatedTokenRepository.exists_by_id(token_id):
                valid = False
                
        except Exception as e:
            logger.info(f"Token introspection failed: {str(e)}")
            valid = False
        
        return IntrospectResponse(valid=valid)
    
    @staticmethod
    def authenticate(request: AuthenticationRequest) -> AuthenticationResponse:
        """
        Authenticate user with email and password
        Returns access token and refresh token
        """
        # Find user by email
        user = UserRepository.find_by_email(request.email)
        if not user:
            raise AppException(ErrorCode.USER_NOT_EXISTED)
        
        # Verify password
        if not bcrypt.check_password_hash(user.password, request.password):
            raise AppException(ErrorCode.UNAUTHENTICATED)
        
        # Generate tokens
        access_token = JWTService.generate_access_token(user)
        refresh_token = JWTService.generate_refresh_token(user)
        
        return AuthenticationResponse(
            message="Thành công",
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    @staticmethod
    def refresh_token(request: RefreshTokenRequest) -> RefreshTokenResponse:
        """
        Refresh access token using refresh token
        Invalidates the old refresh token
        """
        # Verify refresh token
        payload = JWTService.verify_token(request.refresh_token, is_refresh=True)
        
        # Check if refresh token is already invalidated
        token_id = payload.get('jti')
        if InvalidatedTokenRepository.exists_by_id(token_id):
            raise AppException(ErrorCode.UNAUTHENTICATED)
        
        # Invalidate the old refresh token
        expiry_time = datetime.fromtimestamp(payload.get('exp'))
        invalidated = InvalidatedToken(id=token_id, expiry_time=expiry_time)
        InvalidatedTokenRepository.save(invalidated)
        
        # Get user
        user_id = payload.get('sub')
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise AppException(ErrorCode.USER_NOT_EXISTED)
        
        # Generate new tokens
        new_access_token = JWTService.generate_access_token(user)
        new_refresh_token = JWTService.generate_refresh_token(user)
        
        return RefreshTokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    
    @staticmethod
    def logout(request: LogoutRequest) -> None:
        """
        Logout user by invalidating both access and refresh tokens
        """
        # Invalidate access token
        try:
            access_payload = JWTService.verify_token(request.access_token, is_refresh=False)
            access_token_id = access_payload.get('jti')
            access_expiry = datetime.fromtimestamp(access_payload.get('exp'))
            
            InvalidatedTokenRepository.save(
                InvalidatedToken(id=access_token_id, expiry_time=access_expiry)
            )
        except Exception as e:
            logger.info(f"Access token already expired: {str(e)}")
        
        # Invalidate refresh token
        try:
            refresh_payload = JWTService.verify_token(request.refresh_token, is_refresh=True)
            refresh_token_id = refresh_payload.get('jti')
            refresh_expiry = datetime.fromtimestamp(refresh_payload.get('exp'))
            
            InvalidatedTokenRepository.save(
                InvalidatedToken(id=refresh_token_id, expiry_time=refresh_expiry)
            )
        except Exception as e:
            logger.info(f"Refresh token already expired: {str(e)}")

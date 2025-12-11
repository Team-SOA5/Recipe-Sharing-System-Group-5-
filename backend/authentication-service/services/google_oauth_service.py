from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow
from config import Config
from models.models import UserEntity, Role
from repositories.repositories import UserRepository, RoleRepository
from clients.user_profile_client import UserProfileClient
from dto.requests import ProfileCreationRequest
from exceptions.exceptions import AppException, ErrorCode
from constants.constants import PredefinedRole
from utils.jwt_service import JWTService
from extensions import db
import logging
import secrets
import os
import base64
import hashlib
from typing import Optional

# Disable HTTPS requirement for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """Google OAuth service for authentication"""
    
    @staticmethod
    def get_google_auth_url():
        """
        Generate Google OAuth authorization URL
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": Config.GOOGLE_CLIENT_ID,
                    "client_secret": Config.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
                }
            },
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile"
            ]
        )

        flow.redirect_uri = Config.GOOGLE_REDIRECT_URI

        # Enable PKCE for the browser → backend flow
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode("utf-8")

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            code_challenge=code_challenge,
            code_challenge_method='S256'
        )

        return {
            'auth_url': authorization_url,
            'state': state,
            'code_verifier': code_verifier
        }
    
    @staticmethod
    def authenticate_with_google(code: str, code_verifier: Optional[str] = None):
        """
        Authenticate user with Google OAuth code
        Returns access token and refresh token
        """
        try:
            # Exchange authorization code for credentials
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": Config.GOOGLE_CLIENT_ID,
                        "client_secret": Config.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
                    }
                },
                scopes=[
                    "openid",
                    "https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile"
                ]
            )
            
            flow.redirect_uri = Config.GOOGLE_REDIRECT_URI

            # Attach PKCE verifier generated on the frontend (defensive if omitted)
            if code_verifier:
                flow.code_verifier = code_verifier

            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            # Verify the ID token
            id_info = id_token.verify_oauth2_token(
                credentials.id_token,
                requests.Request(),
                Config.GOOGLE_CLIENT_ID
            )
            
            # Extract user information
            google_id = id_info.get('sub')
            email = id_info.get('email')
            name = id_info.get('name', '')
            picture = id_info.get('picture', '')
            
            if not email:
                raise AppException(ErrorCode.UNAUTHENTICATED)
            
            # Check if user already exists
            user = UserRepository.find_by_email(email)
            
            if not user:
                # Create new user with Google account
                user = GoogleOAuthService._create_google_user(
                    email=email,
                    google_id=google_id,
                    name=name,
                    picture=picture
                )
            
            # Generate JWT tokens
            access_token = JWTService.generate_access_token(user)
            refresh_token = JWTService.generate_refresh_token(user)
            
            return {
                'message': 'Thành công',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'email': user.email
                }
            }
            
        except AppException:
            # Re-raise AppException without wrapping
            raise
        except Exception as e:
            logger.error(f"Google OAuth authentication failed: {str(e)}", exc_info=True)
            raise AppException(ErrorCode.UNAUTHENTICATED)
    
    @staticmethod
    def _create_google_user(email: str, google_id: str, name: str, picture: str):
        """
        Create new user from Google OAuth data
        """
        try:
            # Create user entity with random password (won't be used for Google login)
            user = UserEntity()
            user.email = email
            # Generate a random secure password for Google users
            random_password = secrets.token_urlsafe(32)
            from extensions import bcrypt
            user.password = bcrypt.generate_password_hash(random_password).decode('utf-8')
            
            # Assign USER role
            user_role = RoleRepository.find_by_id(PredefinedRole.USER_ROLE)
            if not user_role:
                raise AppException(ErrorCode.ROLE_NOT_EXISTED)
            user.role = [user_role]
            
            # Save user to database
            user = UserRepository.save(user)
            
            # Generate username from email or name
            username = email.split('@')[0]
            # Add random suffix to avoid conflicts
            username = f"{username}_{secrets.token_hex(4)}"
            
            # Create profile in user-service
            profile_request = ProfileCreationRequest(
                id=user.id,
                username=username,
                full_name=name if name else email.split('@')[0],
                email=email
            )
            
            try:
                UserProfileClient.create(profile_request)
            except Exception as e:
                # Rollback user creation if profile creation fails
                logger.error(f"Failed to create user profile for Google user: {str(e)}")
                UserRepository.delete_by_id(user.id)
                raise AppException(ErrorCode.FAIL_REGISTRATION)
            
            logger.info(f"Created new user from Google OAuth: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create Google user: {str(e)}")
            db.session.rollback()
            raise

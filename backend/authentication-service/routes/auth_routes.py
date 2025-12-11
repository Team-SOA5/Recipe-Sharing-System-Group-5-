from flask import Blueprint, request, jsonify
from services.authentication_service import AuthenticationService
from services.user_service import UserService
from services.google_oauth_service import GoogleOAuthService
from dto.requests import (
    AuthenticationRequest, 
    IntrospectRequest, 
    LogoutRequest, 
    RefreshTokenRequest,
    UserCreationRequest
)
from dto.responses import ApiResponse
from exceptions.exceptions import AppException
from utils.validators import validate_email, validate_password, validate_username
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login endpoint - authenticate user
    POST /auth/login
    """
    data = request.get_json()
    
    # Validate request
    email = data.get('email')
    password = data.get('password')
    
    if not email:
        return jsonify({
            'code': 1012,
            'message': 'Điền email',
            'data': None
        }), 400
    
    validate_email(email)
    validate_password(password)
    
    # Authenticate
    auth_request = AuthenticationRequest(email=email, password=password)
    response = AuthenticationService.authenticate(auth_request)
    
    return jsonify({
        'message': response.message,
        'accessToken': response.access_token,
        'refreshToken': response.refresh_token
    }), 200


@auth_bp.route('/refresh-token', methods=['POST'])
def refresh_token():
    """
    Refresh token endpoint
    POST /auth/refresh-token
    """
    data = request.get_json()
    
    refresh_request = RefreshTokenRequest(
        access_token=data.get('accessToken', ''),
        refresh_token=data.get('refreshToken', '')
    )
    
    response = AuthenticationService.refresh_token(refresh_request)
    
    return jsonify({
        'accessToken': response.access_token,
        'refreshToken': response.refresh_token
    }), 200


@auth_bp.route('/introspect', methods=['POST'])
def introspect():
    """
    Introspect token endpoint
    POST /auth/introspect
    """
    data = request.get_json()
    
    introspect_request = IntrospectRequest(
        access_token=data.get('accessToken', '')
    )
    
    response = AuthenticationService.introspect(introspect_request)
    
    return jsonify({
        'code': 0,
        'message': 'Thành công',
        'data': {
            'valid': response.valid
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout endpoint
    POST /auth/logout
    """
    data = request.get_json()
    
    logout_request = LogoutRequest(
        access_token=data.get('accessToken', ''),
        refresh_token=data.get('refreshToken', '')
    )
    
    AuthenticationService.logout(logout_request)
    
    return jsonify({
        'message': 'Thành công'
    }), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register endpoint - create new user
    POST /auth/register
    """
    data = request.get_json()
    
    # Validate request
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    
    if not email:
        return jsonify({
            'code': 1012,
            'message': 'Điền email',
            'data': None
        }), 400
    
    validate_email(email)
    validate_password(password)
    validate_username(username)
    
    # Create user
    user_request = UserCreationRequest(
        email=email,
        password=password,
        username=username,
        full_name=data.get('fullName')
    )
    
    user = UserService.create(user_request)
    
    return jsonify({
        'message': 'Thành công',
        'user': {
            'id': user.id,
            'username': user.username,
            'fullName': user.full_name,
            'avatar': user.avatar,
            'bio': user.bio,
            'recipesCount': user.recipes_count,
            'followersCount': user.followers_count,
            'followingCount': user.following_count,
            'createdAt': user.created_at
        }
    }), 200


@auth_bp.route('/google', methods=['GET'])
def google_login():
    """
    Google OAuth login endpoint - get authorization URL
    GET /auth/google
    """
    try:
        result = GoogleOAuthService.get_google_auth_url()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to generate Google auth URL: {str(e)}")
        return jsonify({
            'code': 1001,
            'message': 'Không thể kết nối với Google',
            'data': None
        }), 500


@auth_bp.route('/google/callback', methods=['POST'])
def google_callback():
    """
    Google OAuth callback endpoint - handle authorization code
    POST /auth/google/callback
    """
    data = request.get_json()
    code = data.get('code')
    code_verifier = data.get('codeVerifier')
    
    if not code or not code_verifier:
        return jsonify({
            'code': 1002,
            'message': 'Thiếu mã xác thực từ Google',
            'data': None
        }), 400
    
    try:
        result = GoogleOAuthService.authenticate_with_google(code, code_verifier)
        return jsonify({
            'message': result['message'],
            'accessToken': result['access_token'],
            'refreshToken': result['refresh_token'],
            'user': result['user']
        }), 200
    except AppException as e:
        logger.error(f"Google OAuth callback failed (AppException): {str(e)}", exc_info=True)
        return jsonify({
            'code': e.error_code.code if hasattr(e, 'error_code') else 1003,
            'message': e.message if hasattr(e, 'message') else 'Đăng nhập Google thất bại',
            'data': None
        }), 401
    except Exception as e:
        logger.error(f"Google OAuth callback failed (Exception): {str(e)}", exc_info=True)
        return jsonify({
            'code': 1003,
            'message': f'Đăng nhập Google thất bại: {str(e)}',
            'data': None
        }), 401

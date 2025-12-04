from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class AuthenticationResponse:
    """Authentication response DTO"""
    message: str
    access_token: str
    refresh_token: str


@dataclass
class IntrospectResponse:
    """Introspect response DTO"""
    valid: bool


@dataclass
class LogoutResponse:
    """Logout response DTO"""
    message: str


@dataclass
class RefreshTokenResponse:
    """Refresh token response DTO"""
    access_token: str
    refresh_token: str


@dataclass
class User:
    """User response DTO"""
    id: str
    username: str
    full_name: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    recipes_count: int = 0
    followers_count: int = 0
    following_count: int = 0
    created_at: Optional[str] = None


@dataclass
class UserDetail:
    """User detail response DTO"""
    id: str
    username: str
    full_name: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    recipes_count: int = 0
    followers_count: int = 0
    following_count: int = 0
    created_at: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    is_following: bool = False


@dataclass
class RegisterResponse:
    """Register response DTO"""
    message: str
    user: User


@dataclass
class ApiResponse:
    """Generic API response wrapper"""
    code: int = 0
    message: str = "Thành công"
    data: Any = None

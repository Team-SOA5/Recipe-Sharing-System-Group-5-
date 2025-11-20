from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthenticationRequest:
    """Authentication request DTO"""
    email: str
    password: str


@dataclass
class UserCreationRequest:
    """User creation request DTO"""
    email: str
    password: str
    username: str
    full_name: Optional[str] = None


@dataclass
class IntrospectRequest:
    """Introspect request DTO"""
    access_token: str


@dataclass
class LogoutRequest:
    """Logout request DTO"""
    access_token: str
    refresh_token: str


@dataclass
class RefreshTokenRequest:
    """Refresh token request DTO"""
    access_token: str
    refresh_token: str


@dataclass
class ProfileCreationRequest:
    """Profile creation request DTO"""
    id: str
    username: str
    full_name: Optional[str]
    email: str

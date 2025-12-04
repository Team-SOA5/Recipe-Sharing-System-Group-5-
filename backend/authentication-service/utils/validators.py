import re
from exceptions.exceptions import AppException, ErrorCode


def validate_email(email: str) -> None:
    """Validate email format"""
    if not email:
        raise AppException(ErrorCode.EMAIL_IS_REQUIRED)
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise AppException(ErrorCode.INVALID_EMAIL)


def validate_password(password: str) -> None:
    """Validate password - minimum 8 characters"""
    if not password or len(password) < 8:
        raise AppException(ErrorCode.INVALID_PASSWORD)


def validate_username(username: str) -> None:
    """Validate username - minimum 5 characters"""
    if not username or len(username) < 5:
        raise AppException(ErrorCode.INVALID_USERNAME)

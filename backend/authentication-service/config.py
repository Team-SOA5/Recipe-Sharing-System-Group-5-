import os
from datetime import timedelta


class Config:
    """Application configuration class"""
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:12345678@localhost:3306/cookpad-identity'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    
    # JWT configuration
    JWT_SIGNER_KEY = os.getenv(
        'JWT_SIGNER_KEY',
        '4vCM6CA5NXhXhG+LjHY+PfQRZYGjm13cHoNxVPuDyEYz2XB5SO/8Ko2vCxBkqHeT'
    )
    JWT_ACCESS_TOKEN_DURATION = int(os.getenv('JWT_ACCESS_TOKEN_DURATION', 1000))  # seconds
    JWT_REFRESH_TOKEN_DURATION = int(os.getenv('JWT_REFRESH_TOKEN_DURATION', 30000))  # seconds
    JWT_ISSUER = 'team16.com'
    
    # Service URLs
    PROFILE_SERVICE_URL = os.getenv(
        'PROFILE_SERVICE_URL',
        'http://localhost:8081/users'
    )
    
    # Application settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JSON_AS_ASCII = False  # Support Vietnamese characters

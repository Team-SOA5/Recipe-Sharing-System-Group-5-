"""
Configuration file for API Gateway
"""

class Config:
    """Base configuration"""
    # Server configuration
    PORT = 8888
    HOST = '0.0.0.0'
    DEBUG = True
    
    # API configuration
    API_PREFIX = '/api/v1'
    
    # Service URLs
    AUTHENTICATION_SERVICE_URL = 'http://localhost:8080'
    USER_SERVICE_URL = 'http://localhost:8081'
    MEDIA_SERVICE_URL = 'http://localhost:8090'
    RECIPE_SERVICE_URL = 'http://localhost:8082'
    CATEGORY_SERVICE_URL = 'http://localhost:8083'
    
    # Public endpoints (regex patterns)
    PUBLIC_ENDPOINTS = [
        r'/auth/.*'
    ]
    
    # CORS settings
    CORS_ORIGINS = '*'
    CORS_METHODS = '*'
    CORS_HEADERS = '*'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

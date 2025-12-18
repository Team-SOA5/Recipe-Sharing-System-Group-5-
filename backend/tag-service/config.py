import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # Server configuration
    SERVER_PORT = int(os.getenv('SERVER_PORT', 8084))
    
    # Application name
    APPLICATION_NAME = os.getenv('APPLICATION_NAME', 'tag-service')
    
    # MongoDB configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://root:root@localhost:27017/tag-service?authSource=admin')
    MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://root:root@localhost:27017/tag-service?authSource=admin')  # For Flask-PyMongo
    MONGODB_AUTO_INDEX_CREATION = os.getenv('MONGODB_AUTO_INDEX_CREATION', 'true').lower() == 'true'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-here')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    
    # Flask configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGODB_URI = os.getenv('TEST_MONGODB_URI', 'mongodb://root:root@localhost:27017/tag-service-test?authSource=admin')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

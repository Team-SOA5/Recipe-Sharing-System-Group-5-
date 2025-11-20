import os
import yaml


class Config:
    """
    Configuration class cho Flask application
    Tương ứng với application.yaml trong Java Spring Boot
    """
    
    # Đọc configuration từ application.yaml
    @staticmethod
    def load_yaml_config():
        """Load configuration từ application.yaml file"""
        config_path = os.path.join(os.path.dirname(__file__), 'application.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    # Load yaml config
    yaml_config = load_yaml_config()
    
    # Server configuration
    SERVER_PORT = yaml_config.get('server', {}).get('port', 8090)
    CONTEXT_PATH = yaml_config.get('server', {}).get('servlet', {}).get('context-path', '/media')
    
    # Application name
    APP_NAME = yaml_config.get('spring', {}).get('application', {}).get('name', 'media-service')
    
    # MongoDB configuration
    mongo_config = yaml_config.get('spring', {}).get('data', {}).get('mongodb', {})
    MONGO_URI = mongo_config.get('uri', 'mongodb://root:root@localhost:27017/file-service?authSource=admin')
    
    # File storage configuration
    app_file_config = yaml_config.get('app', {}).get('file', {})
    FILE_STORAGE_DIR = app_file_config.get('storage-dir', 'media-service/file-storage')
    FILE_DOWNLOAD_PREFIX = app_file_config.get('download-prefix', 'http://localhost:8888/api/v1/media/download/')
    
    # Flask specific
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Max file upload size (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

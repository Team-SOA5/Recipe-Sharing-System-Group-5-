import os
from dotenv import load_dotenv
import yaml

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Load application.yaml
    config_file = os.path.join(os.path.dirname(__file__), 'application.yaml')
    with open(config_file, 'r', encoding='utf-8') as f:
        app_config = yaml.safe_load(f)
    
    # Server configuration
    SERVER_PORT = app_config.get('server', {}).get('port', 8081)
    
    # Application name
    APP_NAME = app_config.get('spring', {}).get('application', {}).get('name', 'user-service')
    
    # Neo4j configuration
    neo4j_config = app_config.get('spring', {}).get('neo4j', {})
    NEO4J_URI = os.getenv('NEO4J_URI', neo4j_config.get('uri', 'bolt://localhost:7687'))
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', neo4j_config.get('authentication', {}).get('username', 'neo4j'))
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', neo4j_config.get('authentication', {}).get('password', '12345678'))
    
    # File service configuration
    file_service = app_config.get('app', {}).get('services', {}).get('file', {})
    DEFAULT_AVATAR = os.getenv('DEFAULT_AVATAR', file_service.get('default-avatar', 'http://localhost:8888/api/v1/media/download/9963eeb2-e8fd-4aef-9585-3f605adc0e7f.png'))
    MEDIA_SERVICE_URL = os.getenv('MEDIA_SERVICE_URL', file_service.get('url', 'http://localhost:8090/media'))
    
    # Recipe service configuration
    recipe_service = app_config.get('app', {}).get('services', {}).get('recipe', {})
    RECIPE_SERVICE_URL = os.getenv('RECIPE_SERVICE_URL', recipe_service.get('url', 'http://localhost:8082'))
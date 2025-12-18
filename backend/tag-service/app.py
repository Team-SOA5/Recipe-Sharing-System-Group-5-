import os
from flask import Flask
from config import config
from extensions import init_extensions
from routes import tag_bp
from exceptions import register_error_handlers


def create_app(config_name=None):
    """
    Application factory pattern
    Equivalent to TagServiceApplication.java main class
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints (routes)
    app.register_blueprint(tag_bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'UP', 'service': 'tag-service'}, 200
    
    @app.route('/', methods=['GET'])
    def index():
        return {
            'service': 'tag-service',
            'version': '1.0.0',
            'status': 'running'
        }, 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = app.config.get('SERVER_PORT', 8084)
    debug = app.config.get('DEBUG', False)
    
    print(f"Starting Tag Service on port {port}...")
    print(f"Debug mode: {debug}")
    print(f"MongoDB URI: {app.config.get('MONGODB_URI')}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

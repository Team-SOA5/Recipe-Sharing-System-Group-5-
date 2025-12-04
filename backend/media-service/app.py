from flask import Flask
from config import Config
from extensions import mongo
from routes.file_routes import file_bp
from exceptions.error_handler import register_error_handlers


def create_app():
    """
    Application factory pattern
    Tạo và cấu hình Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize MongoDB
    mongo.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(file_bp)
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Run application
    # Server port và context path được config trong Config class
    port = Config.SERVER_PORT
    
    print(f"Starting {Config.APP_NAME} on port {port}")
    print(f"Context path: {Config.CONTEXT_PATH}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=Config.DEBUG
    )

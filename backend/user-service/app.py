from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import init_neo4j, close_neo4j
from routes.profile_routes import profile_bp
from routes.internal_routes import internal_bp
from exceptions.error_handler import register_error_handlers
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for frontend
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize Neo4j driver
    init_neo4j(
        uri=config_class.NEO4J_URI,
        username=config_class.NEO4J_USERNAME,
        password=config_class.NEO4J_PASSWORD
    )
    logger.info(f"Neo4j connection initialized: {config_class.NEO4J_URI}")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(profile_bp)
    app.register_blueprint(internal_bp)
    
    # Register cleanup handler
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Close Neo4j driver on app shutdown"""
        close_neo4j()
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting user-service on port {Config.SERVER_PORT}")
    app.run(host='0.0.0.0', port=Config.SERVER_PORT, debug=True)

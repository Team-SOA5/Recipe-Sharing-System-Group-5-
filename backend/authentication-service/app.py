from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from config import Config
from extensions import db, bcrypt
from routes.auth_routes import auth_bp
from exceptions.error_handler import register_error_handlers
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for frontend
    CORS(app, resources={
        r"/auth/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Create tables and initialize data
    with app.app_context():
        db.create_all()
        from utils.init_data import init_application_data
        init_application_data()
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info("Starting authentication-service on port 8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
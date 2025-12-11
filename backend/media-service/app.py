from flask import Flask, send_from_directory
from flask_cors import CORS
from config import app_config
from routes.file_routes import file_bp
from exceptions.error_handler import register_error_handlers
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Register Error Handlers
    register_error_handlers(app)
    
    # Register Blueprint với context path
    # app_config.context_path thường là '/media'
    app.register_blueprint(file_bp, url_prefix=app_config.context_path)
    
    # --- ĐÃ XÓA DÒNG mongo.init_app(app) VÌ KHÔNG CẦN THIẾT ---
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = app_config.port
    print(f"Media Service running at http://localhost:{port}{app_config.context_path}")
    print(f"Storage Directory: {app_config.storage_dir}")
    
    # Debug mode
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import app_config
# from routes.file_routes import file_bp  <-- XÓA DÒNG NÀY Ở ĐÂY (Import quá sớm!)
from exceptions.error_handler import register_error_handlers
from extensions import mongo # <-- Import biến mongo từ extensions
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # 1. Cấu hình App từ config object
    # Flask PyMongo cần đọc MONGO_URI từ app.config
    app.config["MONGO_URI"] = app_config.mongo_uri 
    
    # 2. Khởi tạo Database (BẮT BUỘC PHẢI CÓ)
    # Nếu không có dòng này, mongo.db sẽ luôn là None -> Lỗi TypeError
    mongo.init_app(app)
    
    # 3. Register Error Handlers
    register_error_handlers(app)
    
    # 4. Import và Register Blueprint (Làm ở đây mới an toàn)
    # Import inside function để đảm bảo DB đã init xong mới load routes
    from routes.file_routes import file_bp 
    
    app.register_blueprint(file_bp, url_prefix=app_config.context_path)
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = app_config.port
    print(f"Media Service running at http://localhost:{port}{app_config.context_path}")
    print(f"Storage Directory: {app_config.storage_dir}")
    
    # Debug mode
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
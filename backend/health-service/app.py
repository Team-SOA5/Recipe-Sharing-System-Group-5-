from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from exceptions.exceptions import AppError, ErrorCode

# Load env
load_dotenv()

from routes.health_routes import health_bp

# Config Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# App Config
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 10485760))
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register Routes
app.register_blueprint(health_bp)

# Error Handlers
@app.errorhandler(AppError)
def handle_app_error(e):
    return jsonify({
        "code": e.error_code.code,
        "message": e.message
    }), e.error_code.http_status.value

@app.errorhandler(404)
def not_found(e):
    return jsonify({"code": ErrorCode.NOT_FOUND.code, "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal Error: {e}")
    return jsonify({"code": ErrorCode.UNKNOWN_ERROR.code, "message": "Internal Server Error"}), 500

# Route serve static files (cho Dev environment)
@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8091))
    print(f"Health Service running on port {port}")
    print(f"Auth Mode: SKIP_AUTH={os.getenv('SKIP_AUTH')}")
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG') == 'True')
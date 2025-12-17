from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from exceptions.exceptions import AppError, ErrorCode

load_dotenv()
from routes.ai_routes import ai_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(ai_bp)

# Error Handlers (Tương tự các service khác)
@app.errorhandler(AppError)
def handle_app_error(e):
    return jsonify({"code": e.error_code.code, "message": e.message}), e.error_code.http_status.value

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8092))
    print(f"AI Recommendation Service running on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=True)
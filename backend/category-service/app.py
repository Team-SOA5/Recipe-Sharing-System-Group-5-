from flask import Flask, jsonify
from flask_cors import CORS
from mongoengine import connect
from dotenv import load_dotenv
import os
from routes.category_routes import category_bp

load_dotenv()
app = Flask(__name__)
# Enable CORS for frontend
CORS(app, resources={
    r"/categories/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Kết nối MongoDB
try:
    mongo_uri = os.getenv('MONGO_URI')
    if mongo_uri:
        connect(host=mongo_uri)
    else:
        try:
            connect(host='localhost', port=27017, db='categories-service')
        except:
            connect(
                host='localhost',
                port=27017,
                db='categories-service',
                username=os.getenv('MONGO_USERNAME', 'root'),
                password=os.getenv('MONGO_PASSWORD', 'root'),
                authentication_source=os.getenv('MONGO_AUTH_SOURCE', 'admin')
            )
    print("✅ MongoDB Connected")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")

# Đăng ký Blueprint với prefix /categories
app.register_blueprint(category_bp, url_prefix='/categories')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Category Service Running", "port": os.getenv('PORT', 8083)}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8083))
    app.run(host='0.0.0.0', port=port, debug=True)

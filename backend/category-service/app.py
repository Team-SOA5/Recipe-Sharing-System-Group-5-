from flask import Flask, jsonify
from flask_cors import CORS
from mongoengine import connect
from dotenv import load_dotenv
import os
from routes.category_routes import category_bp

load_dotenv()
app = Flask(__name__)
CORS(app)

# Kết nối MongoDB
try:
    # Sử dụng connect với các tham số riêng biệt để đảm bảo authentication
    mongo_uri = os.getenv('MONGO_URI')
    connect(
        host='localhost',
        port=27017,
        db='categories-service',
        username='root',
        password='root',
        authentication_source='admin'
    )
    print("✅ MongoDB Connected (Category DB)")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")

# Đăng ký Blueprint với prefix /categories
app.register_blueprint(category_bp, url_prefix='/categories')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Category Service Running", "port": os.getenv('PORT')}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8083))
    app.run(host='0.0.0.0', port=port, debug=True)
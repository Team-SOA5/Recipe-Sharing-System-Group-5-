from flask import Flask, jsonify
from flask_cors import CORS
from mongoengine import connect
from dotenv import load_dotenv
import os
from routes.recipe_routes import recipe_bp

load_dotenv()
app = Flask(__name__)
CORS(app)

# Kết nối MongoDB
try:
    connect(host=os.getenv('MONGO_URI'))
    print("✅ MongoDB Connected")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")

# Đăng ký Blueprint
app.register_blueprint(recipe_bp, url_prefix='/recipes')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Recipe Service Running", "port": os.getenv('PORT')}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8082))
    app.run(host='0.0.0.0', port=port, debug=True)
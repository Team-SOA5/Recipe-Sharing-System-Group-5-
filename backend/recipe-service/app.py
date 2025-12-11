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
    mongo_uri = os.getenv('MONGO_URI')
    if mongo_uri:
        connect(host=mongo_uri)
    else:
        try:
            connect(
                host='localhost',
                port=27017,
                db='recipe-service'
            )
        except:
            connect(
                host='localhost',
                port=27017,
                db='recipe-service',
                username=os.getenv('MONGO_USERNAME', 'root'),
                password=os.getenv('MONGO_PASSWORD', 'root'),
                authentication_source=os.getenv('MONGO_AUTH_SOURCE', 'admin')
            )
    print("✅ MongoDB Connected (Recipe DB)")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")

# Đăng ký Blueprint
app.register_blueprint(recipe_bp, url_prefix='/recipes')

from controllers import recipe_controller
@app.route('/users/<userId>/recipes', methods=['GET'])
def user_recipes(userId):
    return recipe_controller.get_recipes_by_user(userId)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Recipe Service Running", "port": os.getenv('PORT')}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8082))
    app.run(host='0.0.0.0', port=port, debug=True)
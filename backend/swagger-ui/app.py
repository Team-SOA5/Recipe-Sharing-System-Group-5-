"""
Swagger UI Service
Provides interactive API documentation for Recipe Sharing System
"""

from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')

# Enable CORS
CORS(app)

# Swagger UI Configuration
SWAGGER_URL = '/api/docs'  # URL for Swagger UI
API_URL = 'http://localhost:5000/static/openapi.yaml'  # OpenAPI spec file path

# Create Swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Recipe Sharing System API",
        'docExpansion': 'list',  # Can be 'none', 'list', or 'full'
        'defaultModelsExpandDepth': 3,
        'defaultModelExpandDepth': 3,
        'displayRequestDuration': True,
        'filter': True,  # Enable filtering
        'showExtensions': True,
        'showCommonExtensions': True,
        'tryItOutEnabled': True,  # Enable "Try it out" by default
    }
)

# Register Swagger UI blueprint
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/')
def index():
    """Redirect to Swagger UI"""
    from flask import redirect
    return redirect(SWAGGER_URL)


@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files (OpenAPI spec)"""
    return send_from_directory('static', path)


@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'swagger-ui',
        'version': '1.0.0'
    }, 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║     Recipe Sharing System - Swagger UI Documentation     ║
    ╚═══════════════════════════════════════════════════════════╝
    
    🚀 Server starting...
    📖 Swagger UI: http://localhost:{port}{SWAGGER_URL}
    🏥 Health check: http://localhost:{port}/health
    
    Press CTRL+C to stop
    """)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

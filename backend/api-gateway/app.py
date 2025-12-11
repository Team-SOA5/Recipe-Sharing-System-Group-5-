from flask import Flask, request, jsonify, Response
import requests
import re
import logging
from functools import wraps
from flask_cors import CORS
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS configuration - Allow all origins, methods, and headers for development
CORS(app, 
     resources={r"/*": {
         "origins": "*",
         "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
         "expose_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True,
         "max_age": 3600
     }})

# Configuration
API_PREFIX = "/api/v1"
PORT = 8888

# Service URLs
SERVICES = {
    "authentication-service": "http://localhost:8080",
    "user-service": "http://localhost:8081",
    "media-service": "http://localhost:8090",
    "recipe-service": "http://localhost:8082",
    "category-service": "http://localhost:8083"
}

# Public endpoints (no authentication required)
PUBLIC_ENDPOINTS = [
    r"/auth/.*"
]


def is_public_endpoint(path):
    """Check if the endpoint is public"""
    for pattern in PUBLIC_ENDPOINTS:
        if re.match(API_PREFIX + pattern, path):
            return True
    return False


def create_api_response(code=0, message="Success!", data=None):
    """Create standardized API response"""
    response = {
        "code": code,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response


def unauthenticated_response():
    """Return unauthenticated response"""
    response = create_api_response(code=1401, message="Unauthenticated")
    return jsonify(response), 401


def introspect_token(token):
    """Call identity service to validate token"""
    try:
        url = f"{SERVICES['authentication-service']}/auth/introspect"
        payload = {"accessToken": token}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("valid", False)
        return False
    except Exception as e:
        logger.error(f"Error introspecting token: {str(e)}")
        return False


def authentication_filter(f):
    """Authentication decorator for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info("Enter authentication filter....")
        
        # Check if endpoint is public
        if is_public_endpoint(request.path):
            return f(*args, **kwargs)
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return unauthenticated_response()
        
        # Extract token
        token = auth_header.replace("Bearer ", "")
        
        # Validate token
        if introspect_token(token):
            return f(*args, **kwargs)
        else:
            return unauthenticated_response()
    
    return decorated_function


def proxy_request(service_url, path, strip_prefix_count=2):
    """Proxy request to target service"""
    # Strip prefix from path
    path_parts = path.split('/')
    # Remove empty strings and first 'strip_prefix_count' parts
    filtered_parts = [p for p in path_parts if p]
    if len(filtered_parts) >= strip_prefix_count:
        target_path = '/' + '/'.join(filtered_parts[strip_prefix_count:])
    else:
        target_path = '/'
    
    # Build target URL
    target_url = f"{service_url}{target_path}"
    
    # Add query parameters if present
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"
    
    # Prepare headers (exclude host header)
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
    
    try:
        # Forward request to target service
        if request.method == 'GET':
            response = requests.get(target_url, headers=headers, timeout=30)
        elif request.method == 'POST':
            response = requests.post(target_url, headers=headers, data=request.get_data(), timeout=30)
        elif request.method == 'PUT':
            response = requests.put(target_url, headers=headers, data=request.get_data(), timeout=30)
        elif request.method == 'DELETE':
            response = requests.delete(target_url, headers=headers, timeout=30)
        elif request.method == 'PATCH':
            response = requests.patch(target_url, headers=headers, data=request.get_data(), timeout=30)
        else:
            return jsonify(create_api_response(code=405, message="Method not allowed")), 405
        
        # Return response
        return Response(
            response.content,
            status=response.status_code,
            headers=dict(response.headers)
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error proxying request to {target_url}: {str(e)}")
        return jsonify(create_api_response(code=500, message=f"Service unavailable: {str(e)}")), 500


# Authentication service routes
@app.route(f'{API_PREFIX}/auth/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def authentication_service(subpath):
    """Route requests to authentication service"""
    return proxy_request(SERVICES['authentication-service'], request.path, strip_prefix_count=2)


# User service routes
@app.route(f'{API_PREFIX}/users/<userId>/recipes', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def user_recipes_service(userId):
    """Route /users/{userId}/recipes to recipe service"""
    return proxy_request(SERVICES['recipe-service'], request.path, strip_prefix_count=2)

@app.route(f'{API_PREFIX}/users/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def user_service(subpath):
    """Route requests to user service"""
    return proxy_request(SERVICES['user-service'], request.path, strip_prefix_count=2)


# Media service routes
@app.route(f'{API_PREFIX}/media/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def media_service(subpath):
    """Route requests to media service"""
    return proxy_request(SERVICES['media-service'], request.path, strip_prefix_count=2)


# Recipe service routes
@app.route(f'{API_PREFIX}/recipes', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], strict_slashes=False)
@app.route(f'{API_PREFIX}/recipes/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def recipe_service_handler(subpath=''):
    """Route requests to recipe service"""
    return proxy_request(SERVICES['recipe-service'], request.path, strip_prefix_count=2)


# Category service routes
@app.route(f'{API_PREFIX}/categories', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], strict_slashes=False)
@app.route(f'{API_PREFIX}/categories/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def category_service_handler(subpath=''):
    """Route requests to category service"""
    return proxy_request(SERVICES['category-service'], request.path, strip_prefix_count=2)


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify(create_api_response(message="API Gateway is running")), 200


if __name__ == '__main__':
    logger.info(f"Starting API Gateway on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True)

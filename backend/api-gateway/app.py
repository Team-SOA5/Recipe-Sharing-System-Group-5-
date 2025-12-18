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
    "category-service": "http://localhost:8083",
    "tag-service": "http://localhost:8084",
    "health-service": "http://localhost:8091",
    "ai-service": "http://localhost:8092",
    # Comment / rating / favorite / follow service
    # Internal routes in this service start with /api/*
    # so we point base URL to /api and strip /api/v1 at the gateway.
    "comment-service": "http://localhost:8085/api",
}

# Public endpoints (no authentication required)
# - /auth/*: authentication & token issuance
# - /media/download/*: cho phép browser tải ảnh/file công khai (avatar, image) không cần gửi Authorization header
PUBLIC_ENDPOINTS = [
    r"/auth/.*",
    r"/media/download/.*"
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
            # DELETE cũng có thể mang body (vd: truyền userId),
            # nên phải forward cả data giống POST/PUT/PATCH
            response = requests.delete(
                target_url,
                headers=headers,
                data=request.get_data(),
                timeout=30
            )
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


# Comment / rating / favorite / follow routes (Comment Service)
@app.route(f'{API_PREFIX}/recipes/<recipe_id>/comments', methods=['GET', 'POST'])
@app.route(f'{API_PREFIX}/comments/<comment_id>', methods=['PUT', 'DELETE'])
@app.route(f'{API_PREFIX}/comments/<comment_id>/like', methods=['POST', 'DELETE'])
@app.route(f'{API_PREFIX}/recipes/<recipe_id>/ratings', methods=['GET', 'POST'])
@app.route(f'{API_PREFIX}/recipes/<recipe_id>/ratings/me', methods=['GET', 'PUT', 'DELETE'])
@app.route(f'{API_PREFIX}/favorites', methods=['GET'])
@app.route(f'{API_PREFIX}/recipes/<recipe_id>/favorite', methods=['POST', 'DELETE'])
@app.route(f'{API_PREFIX}/users/<user_id>/followers', methods=['GET'])
@app.route(f'{API_PREFIX}/users/<user_id>/following', methods=['GET'])
@app.route(f'{API_PREFIX}/users/<user_id>/follow', methods=['POST', 'DELETE'])
@authentication_filter
def comment_service_handler(recipe_id=None, comment_id=None, user_id=None):
    """Route comment/rating/favorite/follow-related requests to comment service"""
    return proxy_request(SERVICES['comment-service'], request.path, strip_prefix_count=2)

# User service routes (other user-related APIs)
@app.route(f'{API_PREFIX}/users/<userId>/recipes', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def user_recipes_service(userId):
    """Route /users/{userId}/recipes to recipe service"""
    return proxy_request(SERVICES['recipe-service'], request.path, strip_prefix_count=2)

@app.route(f'{API_PREFIX}/users/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def user_service(subpath):
    """Route other /users/* requests to user service"""
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


# Tag service routes
@app.route(f'{API_PREFIX}/tags', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], strict_slashes=False)
@app.route(f'{API_PREFIX}/tags/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def tag_service_handler(subpath=''):
    """Route requests to tag service"""
    return proxy_request(SERVICES['tag-service'], request.path, strip_prefix_count=2)


# Health service routes
@app.route(f'{API_PREFIX}/health', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], strict_slashes=False)
@app.route(f'{API_PREFIX}/health/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def health_service_handler(subpath=''):
    """Route requests to health service"""
    return proxy_request(SERVICES['health-service'], request.path, strip_prefix_count=2)


# AI service routes
@app.route(f'{API_PREFIX}/ai', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], strict_slashes=False)
@app.route(f'{API_PREFIX}/ai/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authentication_filter
def ai_service_handler(subpath=''):
    """Route requests to AI service"""
    # Log để debug
    logger.info(f"AI Service Handler - Original path: {request.path}, Subpath: {subpath}")
    # Strip /api/v1, giữ lại /ai/...
    # Nếu subpath có giá trị, dùng nó; nếu không, strip từ path
    if subpath:
        target_path = f'/ai/{subpath}'
    else:
        # Strip /api/v1 từ path
        path_parts = request.path.split('/')
        filtered_parts = [p for p in path_parts if p]
        if len(filtered_parts) >= 2:
            # Bỏ 'api' và 'v1', giữ lại phần còn lại
            target_path = '/' + '/'.join(filtered_parts[2:])
        else:
            target_path = '/ai'
    
    logger.info(f"AI Service Handler - Target path: {target_path}")
    target_url = f"{SERVICES['ai-service']}{target_path}"
    
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
            response = requests.delete(target_url, headers=headers, data=request.get_data(), timeout=30)
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
        logger.error(f"Error proxying to AI service: {str(e)}")
        return jsonify(create_api_response(code=500, message=f"Service unavailable: {str(e)}")), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify(create_api_response(message="API Gateway is running")), 200


if __name__ == '__main__':
    logger.info(f"Starting API Gateway on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True)

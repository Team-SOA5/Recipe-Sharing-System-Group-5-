from flask import Blueprint, request, jsonify
from functools import wraps
from services.tag_service import TagService
from dto.requests import TagRequest
from dto.responses import ApiResponse
from utils.jwt_service import decode_jwt
from exceptions.exceptions import AppException, ErrorCode
from constants.constants import PUBLIC_ENDPOINTS


tag_bp = Blueprint('tag', __name__)


def get_tag_service():
    """Get tag service instance (lazy initialization)"""
    return TagService()


def require_auth(f):
    """
    Decorator for endpoints that require authentication
    Equivalent to Spring Security's authentication filter
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the endpoint is public
        if request.path in PUBLIC_ENDPOINTS:
            return f(*args, **kwargs)
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AppException(ErrorCode.UNAUTHENTICATED)
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode and validate token
            decoded = decode_jwt(token)
            # Store decoded token in request context for use in endpoint
            request.jwt_claims = decoded['claims']
        except AppException:
            raise
        except Exception:
            raise AppException(ErrorCode.UNAUTHENTICATED)
        
        return f(*args, **kwargs)
    
    return decorated_function


@tag_bp.route('/tags', methods=['POST'])
@require_auth
def create_tag():
    """
    Create a new tag or increment count if exists
    Equivalent to TagController.create()
    
    POST /tags
    Request body: {"name": "tag_name"}
    Response: TagResponse with id, name, createdAt, recipesCount
    """
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({
            'code': 400,
            'message': 'Tag name is required'
        }), 400
    
    tag_request = TagRequest.from_dict(data)
    tag_service = get_tag_service()
    tag_response = tag_service.create(tag_request)
    
    return jsonify(tag_response.to_dict()), 200


@tag_bp.route('/tags/popular', methods=['GET'])
def get_popular_tags():
    """
    Get popular tags sorted by recipes count
    Equivalent to TagController.getAllByPopular()
    
    GET /tags/popular?limit=20
    Query params:
        - limit (optional, default=20): Maximum number of tags to return
    Response: TagList with array of TagResponse
    """
    limit = request.args.get('limit', default=20, type=int)
    
    tag_service = get_tag_service()
    tag_list = tag_service.find_by_popular(limit)
    
    return jsonify(tag_list.to_dict()), 200


@tag_bp.route('/tags', methods=['GET'])
def search_tags():
    """
    Search tags by keyword
    Equivalent to TagController.getAllByKey()
    
    GET /tags?search=keyword&limit=20
    Query params:
        - search (required): Keyword to search for
        - limit (optional, default=20): Maximum number of tags to return
    Response: TagList with array of TagResponse
    """
    search = request.args.get('search', type=str)
    limit = request.args.get('limit', default=20, type=int)
    
    if not search:
        return jsonify({
            'code': 400,
            'message': 'Search keyword is required'
        }), 400
    service = get_tag_service()
    tag_
    tag_list = tag_service.find_by_key(search, limit)
    
    return jsonify(tag_list.to_dict()), 200

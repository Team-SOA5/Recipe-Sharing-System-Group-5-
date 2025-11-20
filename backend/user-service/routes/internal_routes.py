from flask import Blueprint, request, jsonify
from services.user_profile_service import UserProfileService
from dto.requests import ProfileCreationRequest
import logging

logger = logging.getLogger(__name__)

# Create Blueprint - equivalent to @RestController with @RequestMapping("/users/internal")
internal_bp = Blueprint('internal', __name__, url_prefix='/users/internal')

# Initialize service
user_profile_service = UserProfileService()


@internal_bp.route('', methods=['POST'])
def create():
    """
    Create a new user profile (internal endpoint)
    Equivalent to Java: @PostMapping
    No authentication required for internal endpoints
    """
    data = request.get_json()
    profile_request = ProfileCreationRequest.from_dict(data)
    user_detail = user_profile_service.create(profile_request)
    return jsonify(user_detail.to_dict()), 201


@internal_bp.route('/<username>', methods=['GET'])
def find_by_username(username):
    """
    Find profile by username (internal endpoint)
    Equivalent to Java: @GetMapping("/{username}")
    No authentication required for internal endpoints
    """
    user_detail = user_profile_service.find_by_username(username)
    return jsonify(user_detail.to_dict()), 200

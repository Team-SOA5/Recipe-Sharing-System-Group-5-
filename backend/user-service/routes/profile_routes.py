from flask import Blueprint, request, jsonify
from services.user_profile_service import UserProfileService
from dto.requests import ProfileUpdationRequest
from utils.jwt_service import jwt_required
import logging

logger = logging.getLogger(__name__)

# Create Blueprint - equivalent to @RestController with @RequestMapping("/users")
profile_bp = Blueprint('profile', __name__, url_prefix='/users')

# Initialize service
user_profile_service = UserProfileService()


@profile_bp.route('/<user_id>', methods=['GET'])
@jwt_required
def find_by_id(user_id):
    """
    Find profile by user ID
    """
    user_detail = user_profile_service.find_by_user_id(user_id)
    return jsonify(user_detail.to_dict()), 200


@profile_bp.route('/me', methods=['GET'])
@jwt_required
def my_profile():
    """
    Get current user's profile
    """
    user_detail = user_profile_service.my_profile()
    return jsonify(user_detail.to_dict()), 200


@profile_bp.route('/me', methods=['PUT'])
@jwt_required
def update_profile():
    """
    Update current user's profile
    """
    data = request.get_json()
    profile_request = ProfileUpdationRequest.from_dict(data)
    user_detail = user_profile_service.update_my_profile(profile_request)
    return jsonify(user_detail.to_dict()), 200


@profile_bp.route('/me/avatar', methods=['PUT'])
@jwt_required
def update_avatar():
    """
    Update current user's avatar
    """
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'code': 1004, 'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({'code': 1004, 'message': 'Empty file'}), 400
    
    user_detail = user_profile_service.update_avatar(file)
    return jsonify(user_detail.to_dict()), 200

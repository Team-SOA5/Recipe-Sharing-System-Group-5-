import requests
from flask import current_app
from typing import Optional, Dict, Any
from dto.requests import ProfileCreationRequest
from dto.responses import UserDetail
import logging

logger = logging.getLogger(__name__)


class UserProfileClient:
    """HTTP client to communicate with user-service - equivalent to Java UserProfileClient"""
    
    @staticmethod
    def create(request: ProfileCreationRequest) -> Optional[UserDetail]:
        """
        Create user profile in user-service
        POST /users/internal
        """
        try:
            url = f"{current_app.config['PROFILE_SERVICE_URL']}/internal"
            data = {
                'id': request.id,
                'username': request.username,
                'fullName': request.full_name,
                'email': request.email
            }
            
            response = requests.post(url, json=data, timeout=5)
            response.raise_for_status()
            
            user_data = response.json()
            return UserProfileClient._parse_user_detail(user_data)
            
        except requests.RequestException as e:
            logger.error(f"Error creating user profile: {str(e)}")
            raise
    
    @staticmethod
    def find_by_username(username: str) -> Optional[UserDetail]:
        """
        Find user profile by username
        GET /users/internal/{username}
        """
        try:
            url = f"{current_app.config['PROFILE_SERVICE_URL']}/internal/{username}"
            
            response = requests.get(url, timeout=5)
            
            # Return None if user not found (404)
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            user_data = response.json()
            return UserProfileClient._parse_user_detail(user_data)
            
        except requests.RequestException as e:
            logger.error(f"Error finding user by username: {str(e)}")
            return None
    
    @staticmethod
    def _parse_user_detail(data: Dict[str, Any]) -> UserDetail:
        """Parse API response to UserDetail object"""
        return UserDetail(
            id=data.get('id', ''),
            username=data.get('username', ''),
            full_name=data.get('fullName', ''),
            avatar=data.get('avatar'),
            bio=data.get('bio'),
            recipes_count=data.get('recipesCount', 0),
            followers_count=data.get('followersCount', 0),
            following_count=data.get('followingCount', 0),
            created_at=data.get('createdAt'),
            email=data.get('email'),
            location=data.get('location'),
            website=data.get('website'),
            is_following=data.get('isFollowing', False)
        )

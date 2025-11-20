from datetime import datetime
from flask import g
from models.models import UserProfile
from dto.requests import ProfileCreationRequest, ProfileUpdationRequest
from dto.responses import UserDetail
from repositories.repositories import UserProfileRepository
from clients.media_client import MediaClient
from exceptions.exceptions import AppException, ErrorCode
from config import Config
import logging

logger = logging.getLogger(__name__)


class UserProfileService:
    """Service layer for user profile operations - equivalent to Java UserProfileService"""
    
    def __init__(self):
        self.repository = UserProfileRepository()
        self.media_client = MediaClient()
        self.default_avatar = Config.DEFAULT_AVATAR
    
    def create(self, request: ProfileCreationRequest) -> UserDetail:
        """
        Create a new user profile
        Equivalent to Java create() method
        """
        # Create UserProfile from request
        user_profile = UserProfile(
            id=request.id,
            username=request.username,
            full_name=request.full_name,
            email=request.email,
            avatar=self.default_avatar,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        saved_profile = self.repository.save(user_profile)
        
        # Convert to UserDetail response
        return UserDetail.from_user_profile(saved_profile)
    
    def update_my_profile(self, request: ProfileUpdationRequest) -> UserDetail:
        """
        Update current user's profile
        Equivalent to Java updateMyProfile() method
        """
        # Get user ID from security context (set by JWT middleware)
        user_id = g.get('user_id')
        if not user_id:
            raise AppException(ErrorCode.UNAUTHENTICATED)
        
        # Find existing profile
        user_profile = self.repository.find_by_id(user_id)
        if not user_profile:
            raise AppException(ErrorCode.PROFILE_NOT_EXISTED)
        
        # Update fields from request
        if request.full_name is not None:
            user_profile.full_name = request.full_name
        if request.bio is not None:
            user_profile.bio = request.bio
        if request.avatar is not None:
            user_profile.avatar = request.avatar
        if request.location is not None:
            user_profile.location = request.location
        if request.website is not None:
            user_profile.website = request.website
        
        # Save updated profile
        saved_profile = self.repository.save(user_profile)
        
        # Convert to UserDetail response
        return UserDetail.from_user_profile(saved_profile)
    
    def update_avatar(self, file) -> UserDetail:
        """
        Update current user's avatar
        Equivalent to Java updateAvatar() method
        """
        # Get user ID from security context
        user_id = g.get('user_id')
        if not user_id:
            raise AppException(ErrorCode.UNAUTHENTICATED)
        
        # Find existing profile
        user_profile = self.repository.find_by_id(user_id)
        if not user_profile:
            raise AppException(ErrorCode.PROFILE_NOT_EXISTED)
        
        # Upload file to media service
        file_response = self.media_client.upload_media(file)
        
        # Update avatar URL
        user_profile.avatar = file_response.url
        
        # Save updated profile
        saved_profile = self.repository.save(user_profile)
        
        # Convert to UserDetail response
        return UserDetail.from_user_profile(saved_profile)
    
    def find_by_user_id(self, user_id: str) -> UserDetail:
        """
        Find user profile by user ID
        Equivalent to Java findByUserId() method
        """
        user_profile = self.repository.find_by_id(user_id)
        if not user_profile:
            raise AppException(ErrorCode.PROFILE_NOT_EXISTED)
        
        return UserDetail.from_user_profile(user_profile)
    
    def find_by_username(self, username: str) -> UserDetail:
        """
        Find user profile by username
        Equivalent to Java findByUsername() method
        """
        user_profile = self.repository.find_by_username(username)
        if not user_profile:
            raise AppException(ErrorCode.PROFILE_NOT_EXISTED)
        
        return UserDetail.from_user_profile(user_profile)
    
    def my_profile(self) -> UserDetail:
        """
        Get current user's profile
        Equivalent to Java myProfile() method
        """
        # Get user ID from security context
        user_id = g.get('user_id')
        if not user_id:
            raise AppException(ErrorCode.UNAUTHENTICATED)
        
        # Find profile
        user_profile = self.repository.find_by_id(user_id)
        if not user_profile:
            raise AppException(ErrorCode.PROFILE_NOT_EXISTED)
        
        return UserDetail.from_user_profile(user_profile)

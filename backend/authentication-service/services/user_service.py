from extensions import bcrypt, db
from models.models import UserEntity, Role
from repositories.repositories import UserRepository, RoleRepository
from dto.requests import UserCreationRequest, ProfileCreationRequest
from dto.responses import User, UserDetail
from exceptions.exceptions import AppException, ErrorCode
from clients.user_profile_client import UserProfileClient
from constants.constants import PredefinedRole
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


class UserService:
    """User service"""
    
    @staticmethod
    def create(request: UserCreationRequest) -> User:
        """
        Create new user and corresponding profile in user-service
        """
        # Check if username already exists in profile service
        existing_profile = UserProfileClient.find_by_username(request.username)
        if existing_profile:
            raise AppException(ErrorCode.USERNAME_EXISTED)
        
        # Create user entity
        user = UserEntity()
        user.email = request.email
        user.password = bcrypt.generate_password_hash(request.password).decode('utf-8')
        
        # Assign USER role
        user_role = RoleRepository.find_by_id(PredefinedRole.USER_ROLE)
        if not user_role:
            raise AppException(ErrorCode.ROLE_NOT_EXISTED)
        user.role = [user_role]
        
        # Save user to database
        try:
            user = UserRepository.save(user)
        except IntegrityError:
            db.session.rollback()
            raise AppException(ErrorCode.USER_EXISTED)
        
        # Create profile in user-service
        profile_request = ProfileCreationRequest(
            id=user.id,
            username=request.username,
            full_name=request.full_name,
            email=request.email
        )
        
        try:
            user_detail = UserProfileClient.create(profile_request)
        except Exception as e:
            # Rollback user creation if profile creation fails
            logger.error(f"Failed to create user profile: {str(e)}")
            UserRepository.delete_by_id(user.id)
            raise AppException(ErrorCode.FAIL_REGISTRATION)
        
        # Convert UserDetail to User response
        return UserService._map_user_detail_to_user(user_detail)
    
    @staticmethod
    def _map_user_detail_to_user(user_detail: UserDetail) -> User:
        """Map UserDetail to User response"""
        return User(
            id=user_detail.id,
            username=user_detail.username,
            full_name=user_detail.full_name,
            avatar=user_detail.avatar,
            bio=user_detail.bio,
            recipes_count=user_detail.recipes_count,
            followers_count=user_detail.followers_count,
            following_count=user_detail.following_count,
            created_at=user_detail.created_at
        )

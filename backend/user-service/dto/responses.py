from typing import Optional, Any, TypeVar, Generic

T = TypeVar('T')

class ApiResponse(Generic[T]):
    """Generic API Response"""
    
    def __init__(self, code: int = 0, message: str = "success!", data: T = None):
        self.code = code
        self.message = message
        self.data = data
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'code': self.code,
            'message': self.message,
            'data': self.data
        }


class UserDetail:
    """Response DTO for user profile details"""
    
    def __init__(
        self,
        id: str = None,
        username: str = None,
        full_name: str = None,
        avatar: str = None,
        bio: str = None,
        recipes_count: int = 0,
        followers_count: int = 0,
        following_count: int = 0,
        created_at: str = None,
        email: str = None,
        location: str = None,
        website: str = None,
        is_following: bool = False
    ):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.avatar = avatar
        self.bio = bio
        self.recipes_count = recipes_count
        self.followers_count = followers_count
        self.following_count = following_count
        self.created_at = created_at
        self.email = email
        self.location = location
        self.website = website
        self.is_following = is_following
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'fullName': self.full_name,
            'avatar': self.avatar,
            'bio': self.bio,
            'recipesCount': self.recipes_count,
            'followersCount': self.followers_count,
            'followingCount': self.following_count,
            'createdAt': self.created_at,
            'email': self.email,
            'location': self.location,
            'website': self.website,
            'isFollowing': self.is_following
        }
    
    @staticmethod
    def from_user_profile(user_profile):
        """Create from UserProfile model"""
        if user_profile is None:
            return None
        
        return UserDetail(
            id=user_profile.id,
            username=user_profile.username,
            full_name=user_profile.full_name,
            avatar=user_profile.avatar,
            bio=user_profile.bio,
            recipes_count=user_profile.recipes_count,
            followers_count=user_profile.followers_count,
            following_count=user_profile.following_count,
            created_at=user_profile.created_at.isoformat() if hasattr(user_profile.created_at, 'isoformat') else user_profile.created_at,
            email=user_profile.email,
            location=user_profile.location,
            website=user_profile.website,
            is_following=user_profile.is_following
        )


class FileResponse:
    """Response DTO from media service"""
    
    def __init__(self, original_file_name: str = None, url: str = None):
        self.original_file_name = original_file_name
        self.url = url
    
    @staticmethod
    def from_dict(data):
        """Create from dictionary"""
        return FileResponse(
            original_file_name=data.get('originalFileName'),
            url=data.get('url')
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'originalFileName': self.original_file_name,
            'url': self.url
        }

from typing import Optional

class ProfileCreationRequest:
    """Request DTO for creating a new profile"""
    
    def __init__(self, id: str, username: str, full_name: str, email: str):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.email = email
    
    @staticmethod
    def from_dict(data):
        """Create from dictionary"""
        return ProfileCreationRequest(
            id=data.get('id'),
            username=data.get('username'),
            full_name=data.get('fullName'),
            email=data.get('email')
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'fullName': self.full_name,
            'email': self.email
        }


class ProfileUpdationRequest:
    """Request DTO for updating profile"""
    
    def __init__(
        self,
        full_name: Optional[str] = None,
        bio: Optional[str] = None,
        avatar: Optional[str] = None,
        location: Optional[str] = None,
        website: Optional[str] = None
    ):
        self.full_name = full_name
        self.bio = bio
        self.avatar = avatar
        self.location = location
        self.website = website
    
    @staticmethod
    def from_dict(data):
        """Create from dictionary"""
        return ProfileUpdationRequest(
            full_name=data.get('fullName'),
            bio=data.get('bio'),
            avatar=data.get('avatar'),
            location=data.get('location'),
            website=data.get('website')
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        result = {}
        if self.full_name is not None:
            result['fullName'] = self.full_name
        if self.bio is not None:
            result['bio'] = self.bio
        if self.avatar is not None:
            result['avatar'] = self.avatar
        if self.location is not None:
            result['location'] = self.location
        if self.website is not None:
            result['website'] = self.website
        return result


class GetProfileRequest:
    """Request DTO for getting profile (if needed)"""
    
    def __init__(self, user_id: str = None, username: str = None):
        self.user_id = user_id
        self.username = username
    
    @staticmethod
    def from_dict(data):
        """Create from dictionary"""
        return GetProfileRequest(
            user_id=data.get('userId'),
            username=data.get('username')
        )

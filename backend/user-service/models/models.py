from datetime import datetime
from typing import Optional

class UserProfile:
    """User Profile Model - represents a node in Neo4j"""
    
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
        created_at: datetime = None,
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
        self.created_at = created_at or datetime.utcnow()
        self.email = email
        self.location = location
        self.website = website
        self.is_following = is_following
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'fullName': self.full_name,
            'avatar': self.avatar,
            'bio': self.bio,
            'recipesCount': self.recipes_count,
            'followersCount': self.followers_count,
            'followingCount': self.following_count,
            'createdAt': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'email': self.email,
            'location': self.location,
            'website': self.website,
            'isFollowing': self.is_following
        }
    
    @staticmethod
    def from_neo4j_node(node):
        """Create UserProfile from Neo4j node"""
        if node is None:
            return None
        
        props = dict(node)
        return UserProfile(
            id=props.get('id'),
            username=props.get('username'),
            full_name=props.get('fullName'),
            avatar=props.get('avatar'),
            bio=props.get('bio'),
            recipes_count=props.get('recipesCount', 0),
            followers_count=props.get('followersCount', 0),
            following_count=props.get('followingCount', 0),
            created_at=props.get('createdAt'),
            email=props.get('email'),
            location=props.get('location'),
            website=props.get('website'),
            is_following=props.get('isFollowing', False)
        )
    
    def to_neo4j_properties(self):
        """Convert model to Neo4j properties"""
        return {
            'id': self.id,
            'username': self.username,
            'fullName': self.full_name,
            'avatar': self.avatar,
            'bio': self.bio,
            'recipesCount': self.recipes_count,
            'followersCount': self.followers_count,
            'followingCount': self.following_count,
            'createdAt': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'email': self.email,
            'location': self.location,
            'website': self.website,
            'isFollowing': self.is_following
        }

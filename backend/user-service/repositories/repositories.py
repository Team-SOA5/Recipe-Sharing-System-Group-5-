from typing import Optional
from extensions import get_neo4j_driver
from models.models import UserProfile
import logging

logger = logging.getLogger(__name__)


class UserProfileRepository:
    """Repository for UserProfile operations with Neo4j"""
    
    def __init__(self):
        pass
    
    def _get_driver(self):
        """Get Neo4j driver instance"""
        driver = get_neo4j_driver()
        if driver is None:
            raise Exception("Neo4j driver not initialized. Please check the connection.")
        return driver
    
    def save(self, user_profile: UserProfile) -> UserProfile:
        """
        Save or update a user profile in Neo4j
        Uses MERGE to create or update the node
        """
        with self._get_driver().session() as session:
            result = session.execute_write(self._save_user_profile, user_profile)
            return result
    
    @staticmethod
    def _save_user_profile(tx, user_profile: UserProfile):
        """Transaction function to save user profile"""
        props = user_profile.to_neo4j_properties()
        
        query = """
        MERGE (u:`user-profile` {id: $id})
        SET u.username = $username,
            u.fullName = $fullName,
            u.avatar = $avatar,
            u.bio = $bio,
            u.recipesCount = $recipesCount,
            u.followersCount = $followersCount,
            u.followingCount = $followingCount,
            u.createdAt = $createdAt,
            u.email = $email,
            u.location = $location,
            u.website = $website,
            u.isFollowing = $isFollowing
        RETURN u
        """
        
        result = tx.run(query, **props)
        record = result.single()
        if record:
            return UserProfile.from_neo4j_node(record['u'])
        return None
    
    def find_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Find user profile by ID"""
        with self._get_driver().session() as session:
            result = session.execute_read(self._find_by_id, user_id)
            return result
    
    @staticmethod
    def _find_by_id(tx, user_id: str):
        """Transaction function to find user by ID"""
        query = """
        MATCH (u:`user-profile` {id: $id})
        RETURN u
        """
        result = tx.run(query, id=user_id)
        record = result.single()
        if record:
            return UserProfile.from_neo4j_node(record['u'])
        return None
    
    def find_by_username(self, username: str) -> Optional[UserProfile]:
        """Find user profile by username"""
        with self._get_driver().session() as session:
            result = session.execute_read(self._find_by_username, username)
            return result
    
    @staticmethod
    def _find_by_username(tx, username: str):
        """Transaction function to find user by username"""
        query = """
        MATCH (u:`user-profile` {username: $username})
        RETURN u
        """
        result = tx.run(query, username=username)
        record = result.single()
        if record:
            return UserProfile.from_neo4j_node(record['u'])
        return None
    
    def delete_by_id(self, user_id: str) -> bool:
        """Delete user profile by ID"""
        with self._get_driver().session() as session:
            result = session.execute_write(self._delete_by_id, user_id)
            return result
    
    @staticmethod
    def _delete_by_id(tx, user_id: str):
        """Transaction function to delete user by ID"""
        query = """
        MATCH (u:`user-profile` {id: $id})
        DELETE u
        RETURN count(u) as deleted
        """
        result = tx.run(query, id=user_id)
        record = result.single()
        return record['deleted'] > 0 if record else False

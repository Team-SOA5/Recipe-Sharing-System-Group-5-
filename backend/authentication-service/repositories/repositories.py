from extensions import db
from models.models import UserEntity, Role, InvalidatedToken
from typing import Optional


class UserRepository:
    """Repository for UserEntity - equivalent to Java UserRepository"""
    
    @staticmethod
    def find_by_email(email: str) -> Optional[UserEntity]:
        """Find user by email"""
        return UserEntity.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_id(user_id: str) -> Optional[UserEntity]:
        """Find user by ID"""
        return UserEntity.query.get(user_id)
    
    @staticmethod
    def save(user: UserEntity) -> UserEntity:
        """Save user entity"""
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def delete_by_id(user_id: str) -> None:
        """Delete user by ID"""
        user = UserEntity.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
    
    @staticmethod
    def exists_by_email(email: str) -> bool:
        """Check if user exists by email"""
        return UserEntity.query.filter_by(email=email).first() is not None


class RoleRepository:
    """Repository for Role - equivalent to Java RoleRepository"""
    
    @staticmethod
    def find_by_id(name: str) -> Optional[Role]:
        """Find role by name (name is the ID)"""
        return Role.query.get(name)
    
    @staticmethod
    def save(role: Role) -> Role:
        """Save role entity"""
        db.session.add(role)
        db.session.commit()
        return role
    
    @staticmethod
    def save_all(roles: list) -> None:
        """Save multiple roles"""
        db.session.add_all(roles)
        db.session.commit()
    
    @staticmethod
    def count() -> int:
        """Count total roles"""
        return Role.query.count()


class InvalidatedTokenRepository:
    """Repository for InvalidatedToken - equivalent to Java InvalidatedTokenRepository"""
    
    @staticmethod
    def save(token: InvalidatedToken) -> InvalidatedToken:
        """Save invalidated token"""
        db.session.add(token)
        db.session.commit()
        return token
    
    @staticmethod
    def exists_by_id(token_id: str) -> bool:
        """Check if token is invalidated"""
        return InvalidatedToken.query.get(token_id) is not None
    
    @staticmethod
    def find_by_id(token_id: str) -> Optional[InvalidatedToken]:
        """Find invalidated token by ID"""
        return InvalidatedToken.query.get(token_id)

from extensions import db
from datetime import datetime
import uuid


# Association table for many-to-many relationship between User and Role
user_roles = db.Table('user_entity_role',
    db.Column('user_entity_id', db.String(255), db.ForeignKey('user_entity.id'), primary_key=True),
    db.Column('role_name', db.String(255), db.ForeignKey('role.name'), primary_key=True)
)


class UserEntity(db.Model):
    """User entity model"""
    __tablename__ = 'user_entity'
    
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(
        db.String(255, collation='utf8mb4_unicode_ci'),
        unique=True,
        nullable=False,
        index=True
    )
    password = db.Column(db.String(255), nullable=False)
    
    # Many-to-many relationship with Role
    role = db.relationship('Role', secondary=user_roles, backref='users', lazy='joined')
    
    def __repr__(self):
        return f'<UserEntity {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email
        }


class Role(db.Model):
    """Role entity model"""
    __tablename__ = 'role'
    
    name = db.Column(db.String(255), primary_key=True)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description
        }


class InvalidatedToken(db.Model):
    """Invalidated token entity model"""
    __tablename__ = 'invalidated_token'
    
    id = db.Column(db.String(255), primary_key=True)
    expiry_time = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<InvalidatedToken {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'expiry_time': self.expiry_time.isoformat() if self.expiry_time else None
        }

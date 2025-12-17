import pickle
from datetime import datetime

from extensions import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(255), primary_key=True)
    username = db.Column(db.String(255), unique=True)
    full_name = db.Column(db.String(255))
    avatar = db.Column(db.String(255))
    bio = db.Column(db.String(255))
    recipes_count = db.Column(db.Integer)
    followers_count = db.Column(db.Integer)
    following_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

    def __init__(self, username: str, full_name: str, avatar: str, bio: str, recipes_count: str,
                 followers_count: str, following_count: str, created_at: str):
        self.username = username
        self.full_name = full_name
        self.avatar = avatar
        self.bio = bio
        self.recipes_count = recipes_count
        self.followers_count = followers_count
        self.following_count = following_count
        self.created_at = created_at

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "avatar": self.avatar,
            "bio": self.bio,
            "recipes_count": self.recipes_count,
            "followers_count": self.followers_count,
            "following_count": self.following_count,
            "created_at": self.created_at
        }


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.String(255), primary_key=True)
    recipe_id = db.Column(db.String(255), unique=True)
    content = db.Column(db.String(255))
    author = db.Column(db.String(255)) # more like db.Column(db.String, db.ForeignKey('users.id'))?
    images = db.Column(db.LargeBinary) # actually a list[str] underneath!
    likes_count = db.Column(db.Integer)
    is_liked = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, id: str, recipe_id: str, content: str, author: str, images: list[str],
                 likes_count: int, is_liked: bool, created_at: datetime, updated_at: datetime):
        self.id = id
        self.recipe_id = recipe_id
        self.content = content
        self.author = author
        self.images = pickle.dumps(images)
        self.likes_count = likes_count
        self.is_liked = is_liked
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "content": self.content,
            "author": db.session.get(User, self.author).to_dict(),
            "images": pickle.loads(self.images),
            "likes_count": self.likes_count,
            "is_liked": self.is_liked,
            "created_at": self.created_at.strftime("%d-%m-%Y %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%d-%m-%Y %H:%M:%S")
        }

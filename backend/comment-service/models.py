import pickle
from dataclasses import dataclass
from datetime import datetime

from databases import db


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(255), primary_key=True)
    username = db.Column(db.String(255), unique=True)
    full_name = db.Column(db.String(255))
    avatar = db.Column(db.String(255))
    bio = db.Column(db.String(255))
    recipes_count = db.Column(db.Integer)
    follower_ids = db.Column(db.LargeBinary) # list[User.id]
    created_at = db.Column(db.DateTime)

    def __init__(self, user_id: str, username: str, full_name: str, avatar: str, bio: str, recipes_count: str,
                 followers: list[str], created_at: str):
        self.user_id = user_id
        self.username = username
        self.full_name = full_name
        self.avatar = avatar
        self.bio = bio
        self.recipes_count = recipes_count
        self.follower_ids = pickle.dumps(followers)
        self.created_at = created_at

    def get_followers_count(self):
        return len(pickle.loads(self.follower_ids))

    def get_following_count(self):
        return len([u for u in pickle.loads(self.follower_ids) if u.is_favorited_by(self.user_id)])

    def accept_follow_by(self, user_id: str):
        follower_ids: list[str] = pickle.loads(self.follower_ids)

        if user_id not in follower_ids:
            follower_ids.append(user_id)

        self.follower_ids = pickle.dumps(follower_ids)

    def accept_unfollow_by(self, user_id: str):
        follower_ids: list[str] = pickle.loads(self.follower_ids)
        follower_ids.remove(user_id)
        self.follower_ids = pickle.dumps(follower_ids)

    def is_favorited_by(self, user_id: str):
        follower_ids: list[str] = pickle.loads(self.follower_ids)
        return user_id in follower_ids

    def to_dict(self):
        users: list[User] = User.query.all()

        return {
            "user_id": self.user_id,
            "username": self.username,
            "full_name": self.full_name,
            "avatar": self.avatar,
            "bio": self.bio,
            "recipes_count": self.recipes_count,
            "followers_count": len(pickle.loads(self.follower_ids)),
            "following_count": len([u for u in users if u.is_favorited_by(self.user_id)]),
            "created_at": self.created_at
        }


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.String(255), primary_key=True)
    # Một recipe có thể có nhiều comment, không nên unique
    recipe_id = db.Column(db.String(255), index=True)
    content = db.Column(db.String(255))
    author = db.Column(db.String(255)) # User.id
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

    def to_dict(self):
        return {
            "id": self.id,
            "recipe_id": self.recipe_id,
            "content": self.content,
            "author": self.author,
            "images": pickle.loads(self.images),
            "likes_count": self.likes_count,
            "is_liked": self.is_liked,
            "created_at": self.created_at.strftime("%d-%m-%Y %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%d-%m-%Y %H:%M:%S")
        }


class Rating(db.Model):
    __tablename__ = 'ratings'
    # primary key riêng cho rating
    id = db.Column(db.String(255), primary_key=True)
    # liên kết tới recipe
    recipe_id = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer)
    review = db.Column(db.String(255))
    author = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, id: str | None, recipe_id: str, rating: int, review: str, author: str,
                 created_at: datetime, updated_at: datetime):
        self.id = id
        self.recipe_id = recipe_id
        self.rating = rating
        self.review = review
        self.author = author
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "review": self.review,
            "author": self.author,
            "created_at": self.created_at.strftime("%d-%m-%Y %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%d-%m-%Y %H:%M:%S")
        }


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    icon = db.Column(db.String(255))
    recipes_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

    def __init__(self, id: str, name: str, description: str, icon: str, recipes_count: int, created_at: datetime):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.recipes_count = recipes_count
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "recipesCount": self.recipes_count,
            "createdAt": self.created_at.strftime("%d-%m-%Y %H:%M:%S"),
        }


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    recipes_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

    def __init__(self, id: str, name: str, recipes_count: int, created_at: datetime):
        self.id = id
        self.name = name
        self.recipes_count = recipes_count
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "recipesCount": self.recipes_count,
            "createdAt": self.created_at
        }


class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    thumbnail = db.Column(db.String(255)) # Uri
    author = db.Column(db.String(255))
    category = db.Column(db.String(255))
    difficulty = db.Column(db.String(255)) # 'easy' | 'medium' | 'hard'
    cooking_time = db.Column(db.Integer)
    servings = db.Column(db.Integer)
    average_ratings = db.Column(db.Float)
    ratings_count = db.Column(db.Integer)
    favorited_user_ids = db.Column(db.LargeBinary) # list[User.id]

    def __init__(self, id: str, title: str, description: str, thumbnail: str, author: str,
                 category: str, difficulty: str, cooking_time: int, ratings_count: int,
                 servings: int, average_ratings: float, rating_count: int, favorited_user_ids: list[str]):
        self.id = id
        self.title = title
        self.description = description
        self.thumbnail = thumbnail
        self.author = author
        self.category = category
        self.difficulty = difficulty
        self.cooking_time = cooking_time
        self.ratings_count = ratings_count
        self.servings = servings
        self.average_ratings = average_ratings
        self.rating_count = rating_count
        self.favorited_user_ids = pickle.dumps(favorited_user_ids)

    def set_as_favorite_of(self, user_id: str):
        favorited_user_ids: list[str] = pickle.loads(self.favorited_user_ids)

        if user_id not in favorited_user_ids:
            favorited_user_ids.append(user_id)

        self.favorited_user_ids = pickle.dumps(favorited_user_ids)

    def unset_as_favorite_of(self, user_id: str):
        """Bỏ đánh dấu yêu thích của một user nếu có."""
        favorited_user_ids: list[str] = pickle.loads(self.favorited_user_ids)
        if user_id in favorited_user_ids:
            favorited_user_ids.remove(user_id)
            self.favorited_user_ids = pickle.dumps(favorited_user_ids)

    def is_favorited_by(self, user_id: str):
        favorited_user_ids: list[str] = pickle.loads(self.favorited_user_ids)
        return user_id in favorited_user_ids

    def to_dict(self):
        favorited_user_ids: list[str] = pickle.loads(self.favorited_user_ids)
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "author": self.author,
            "category": self.category,
            "difficulty": self.difficulty,
            "cookingTime": self.cooking_time,
            "ratingsCount": self.ratings_count,
            "servings": self.servings,
            "averageRatings": self.average_ratings,
            # Frontend có thể dùng cả hai key, đều map từ ratings_count
            "ratingCount": self.ratings_count,
            "favoritesCount": len(favorited_user_ids),
            "favoritedUserIds": favorited_user_ids,
        }

    def to_dict_for(self, user_id: str):
        favorited_user_ids: list[str] = pickle.loads(self.favorited_user_ids)

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "author": self.author,
            "category": self.category,
            "difficulty": self.difficulty,
            "cookingTime": self.cooking_time,
            "ratingsCount": self.ratings_count,
            "servings": self.servings,
            "averageRatings": self.average_ratings,
            "ratingCount": self.ratings_count,
            "favoritesCount": len(favorited_user_ids),
            "isFavorited": user_id in favorited_user_ids
        }

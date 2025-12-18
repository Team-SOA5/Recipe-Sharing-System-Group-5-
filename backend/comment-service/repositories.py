from databases import db
from models import *


class UserRepository:
    @staticmethod
    def get_by_id(id: str) -> User:
        return User.query.filter_by(user_id=id).first()

    @staticmethod
    def all() -> list[User]:
        return User.query.all()

    @staticmethod
    def get_followers_of(user_id: str, page: int, limit_per_page: int) -> list[User]:
        users: list[User] = (User.query.filter_by(user_id=user_id)
                             .paginate(page=page, per_page=limit_per_page, error_out=False))

        return users

    @staticmethod
    def get_users_following(user_id: str, page: int, limit_per_page: int) -> list[User]:
        users: list[User] = (User.query.filter_by(user_id=user_id)
                             .paginate(page=page, per_page=limit_per_page, error_out=False))

        return users

    @staticmethod
    def save(user: User):
        db.session.add(user)
        db.session.commit()


class CommentRepository:
    @staticmethod
    def get_all_comments() -> list[Comment]:
        return db.session.query(Comment).all()

    @staticmethod
    def get_by_id(id: str) -> Comment:
        return Comment.query.filter_by(id=id).first()

    @staticmethod
    def get_comments_to_recipe(recipe_id: str, page: int, limit_per_page: int,
                               sorting_criteria: str) -> list[Comment]:
        comments: list[Comment] = Comment.query.paginate(page=page, per_page=limit_per_page, error_out=False)
        result: list[Comment] = [c for c in comments if c.recipe_id == recipe_id]

        if sorting_criteria == "newest":
            result.sort(key=lambda c: c.created_at, reverse=True)
        elif sorting_criteria == "oldest":
            result.sort(key=lambda c: c.created_at, reverse=False)
        elif sorting_criteria == "most_liked":
            result.sort(key=lambda c: c.likes_count, reverse=True)
        else:
            raise Exception(f"Unknown sorting criteria '{sorting_criteria}'!")

        return result

    @staticmethod
    def save(comment: Comment):
        db.session.add(comment)
        db.session.commit()

    @staticmethod
    def delete(comment: Comment):
        db.session.delete(comment)
        db.session.commit()


class RatingRepository:
    @staticmethod
    def get_by_id(id: str) -> Rating:
        return Rating.query.filter_by(id=id).first()

    @staticmethod
    def get_by_user_id(user_id: str) -> list[Rating]:
        return Rating.query.filter_by(author=user_id).all()

    @staticmethod
    def get_by_author_id_and_recipe_id(author_id: str, recipe_id: str) -> Rating:
        return Rating.query.filter_by(author=author_id, recipe_id=recipe_id).first()

    @staticmethod
    def get_all_of_recipe_id(recipe_id: str) -> list[Rating]:
        return list(Rating.query.filter_by(recipe_id=recipe_id).all())

    @staticmethod
    def save(rating: Rating):
        db.session.add(rating)
        db.session.commit()

    @staticmethod
    def delete(rating: Rating):
        db.session.delete(rating)
        db.session.commit()


class RecipeRepository:
    @staticmethod
    def get_by_id(id: str) -> Recipe:
        return Recipe.query.filter_by(id=id).first()

    @staticmethod
    def get_liked_recipes_of(user_id: str, page: int, limit_per_page: int) -> list[Recipe]:
        recipes: list[Recipe] = Recipe.query.paginate(page=page, per_page=limit_per_page, error_out=False)
        return [r for r in recipes if r.is_favorited_by(user_id)]

    @staticmethod
    def save(recipe: Recipe):
        db.session.add(recipe)
        db.session.commit()

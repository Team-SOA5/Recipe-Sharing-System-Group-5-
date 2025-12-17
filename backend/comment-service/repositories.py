from extensions import db
from models import Comment

class CommentRepository:
    @staticmethod
    def get_all_comments() -> list[Comment]:
        return db.session.query(Comment).all()

    @staticmethod
    def get_comment_by_id(comment_id: str) -> Comment:
        return Comment.query.filter_by(id=comment_id).first()

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
    def save_comment(comment: Comment):
        db.session.add(comment)
        db.session.commit()

    @staticmethod
    def delete_comment(comment: Comment):
        db.session.delete(comment)
        db.session.commit()

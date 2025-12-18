from flask import Blueprint, request, jsonify, g

from helpers import make_random_string
from repositories import *


bp = Blueprint('socials', __name__)


def __get_current_user_id() -> str | None:
    return g.get('user_id')


def __get_current_user() -> User | None:
    user_id = __get_current_user_id()
    return User.query.get(user_id) if user_id else None


# comments service
@bp.route('/api/recipes/<recipe_id>/comments', methods=['GET'])
def get_comments_of_recipe(recipe_id: str):
    queries = request.args
    page = int(queries.get('page', 1))
    limit = int(queries.get('limit', 20))
    sort = queries.get('sort', 'newest')
    comments = CommentRepository.get_comments_to_recipe(recipe_id, page, limit, sort)
    return jsonify([c.to_dict() for c in comments]), 200


@bp.route('/api/recipes/<recipe_id>/comments', methods=['POST'])
def post_comment_of_recipe(recipe_id: str):
    queries = request.args
    body = request.get_json()
    content: str = body['content']
    images: list[str] = body['images']
    author_id: str = g.get('user_id')
    now = datetime.now()
    comment_id = make_random_string(16)

    comment = Comment(comment_id, recipe_id, content, author_id, images,
                      0, False, now, now)

    CommentRepository.save(comment)
    return jsonify(comment.to_dict()), 200


@bp.route('/api/comments/<comment_id>', methods=['PUT'])
def update_comment(comment_id: str):
    queries = request.args
    body = request.get_json()
    comment = CommentRepository.get_by_id(comment_id)
    comment.content = body['content']
    comment.author = body['author']
    comment.images = pickle.dumps(body['images'])
    comment.updated_at = datetime.now()
    CommentRepository.save(comment)
    return jsonify(comment.to_dict()), 200


@bp.route('/api/comments/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id: str):
    CommentRepository.delete(CommentRepository.get_by_id(comment_id))
    return jsonify(), 200


@bp.route('/api/comments/<comment_id>/like', methods=['POST'])
def like_comment(comment_id: str):
    comment = CommentRepository.get_by_id(comment_id)
    comment.is_liked = True
    comment.likes_count += 1
    CommentRepository.save(comment)
    return jsonify({ "liked": True, "likesCount": comment.likes_count }), 200


@bp.route('/api/comments/<comment_id>/like', methods=['DELETE'])
def unlike_comment(comment_id: str):
    comment = CommentRepository.get_by_id(comment_id)
    comment.is_liked = False
    comment.likes_count -= 1
    CommentRepository.save(comment)
    return jsonify({ "liked": False, "likesCount": comment.likes_count }), 200


# ratings service
@bp.route('/api/recipes/<recipe_id>/ratings', methods=['GET'])
def get_ratings_of_recipe(recipe_id: str):
    ratings = RatingRepository.get_all_of_recipe_id(recipe_id)
    return jsonify([r.to_dict() for r in ratings]), 200


@bp.route('/api/recipes/<recipe_id>/ratings', methods=['POST'])
def post_ratings_of_recipe(recipe_id: str):
    queries = request.args
    body = request.get_json()
    rating: int = body['rating'] # TODO: Constrain down to [1, 5]!
    review: str = body['review']
    author_id: str = g.get('user_id')
    created_at: datetime = datetime.now()
    result = Rating(recipe_id, rating, review, author_id, created_at, created_at)
    RatingRepository.save(result)
    return jsonify(RatingRepository.get_by_author_id_and_recipe_id(author_id, recipe_id).to_dict()), 200


@bp.route('/api/recipes/<recipe_id>/ratings/me', methods=['GET'])
def get_my_ratings_of_recipe(recipe_id: str):
    user_id = g.get('user_id')
    result = RatingRepository.get_by_author_id_and_recipe_id(user_id, recipe_id)
    return jsonify(result.to_dict()), 200


@bp.route('/api/recipes/<recipe_id>/ratings/me', methods=['PUT'])
def put_my_ratings_of_recipe(recipe_id: str):
    queries = request.args
    body = request.get_json()
    rating: int = body['rating']  # TODO: Constrain down to [1, 5]!
    review: str = body['review']
    author_id: str = g.get('user_id')
    updated_at: datetime = datetime.now()
    result = RatingRepository.get_by_author_id_and_recipe_id(author_id, recipe_id)
    result.rating = rating
    result.review = review
    result.updated_at = updated_at
    RatingRepository.save(result)
    return jsonify(result.to_dict()), 200


@bp.route('/api/recipes/<recipe_id>/ratings/me', methods=['DELETE'])
def delete_my_ratings_of_recipe(recipe_id: str):
    author_id = g.get('user_id')
    rating = RatingRepository.get_by_author_id_and_recipe_id(author_id, recipe_id)
    RatingRepository.delete(rating)
    return jsonify(), 200


# favorites service
@bp.route('/api/users/<user_id>/favorites', methods=['DELETE'])
def get_favorite_recipes_of_user(user_id: str):
    queries = request.args
    body = request.get_json()
    page: int = queries.get('page', 1)
    limit: int = queries.get('limit', 20)
    recipes = RecipeRepository.get_liked_recipes_of(user_id, page, limit)
    return jsonify([r.to_dict_for(user_id) for r in recipes]), 200


@bp.route('/api/favorites', methods=['GET'])
def get_favorite_recipes_of_me():
    return get_favorite_recipes_of_user(__get_current_user_id())


@bp.route('/api/recipes/<recipe_id>/favorite', methods=['POST'])
def favorite_recipe(recipe_id: str):
    recipe = RecipeRepository.get_by_id(recipe_id)
    recipe.set_as_favorite_of(__get_current_user_id())
    RecipeRepository.save(recipe)
    return jsonify(), 200


@bp.route('/api/recipes/<recipe_id>/favorite', methods=['DELETE'])
def unfavorite_recipe(recipe_id: str):
    recipe = RecipeRepository.get_by_id(recipe_id)
    recipe.unset_as_favorite_of(__get_current_user_id())
    RecipeRepository.save(recipe)
    return jsonify(), 200


# follow service
@bp.route('/api/users/<user_id>/followers', methods=['GET'])
def get_followers_of_user(user_id: str):
    queries = request.args
    page: int = queries.get('page', 1)
    limit: int = queries.get('limit', 20)
    result: list[User] = UserRepository.get_followers_of(user_id, page, limit)
    return jsonify([u.to_dict() for u in result]), 200


@bp.route('/api/users/<user_id>/followers', methods=['GET'])
def get_followings_of_user(user_id: str):
    queries = request.args
    page: int = queries.get('page', 1)
    limit: int = queries.get('limit', 20)
    result: list[User] = UserRepository.get_users_following(user_id, page, limit)
    return jsonify([u.to_dict() for u in result]), 200


@bp.route('/api/users/<user_id>/follow', methods=['POST'])
def follow_user(user_id: str):
    current_user_id = __get_current_user_id()
    user = UserRepository.get_by_id(current_user_id)
    user.accept_follow_by(user_id)
    UserRepository.save(user)

    return jsonify({
        "following": True,
        "followersCount": user.get_followers_count() + 1
    }), 200


@bp.route('/api/users/<user_id>/follow', methods=['DELETE'])
def unfollow_user(user_id: str):
    current_user_id = __get_current_user_id()
    user = UserRepository.get_by_id(user_id)
    user.accept_unfollow_by(current_user_id)
    UserRepository.save(user)

    return jsonify({
        "following": False,
        "followersCount": user.get_followers_count() - 1
    }), 200

# notification service


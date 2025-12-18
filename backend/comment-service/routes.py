import requests
from flask import Blueprint, request, jsonify, g
from requests import RequestException

from helpers import make_random_string
from repositories import *


bp = Blueprint('socials', __name__)


def __get_current_user_id() -> str | None:
    return g.user_id


def __get_current_user():
    path = f"https://localhost:8081/api/users/me"

    try:
        result: dict = requests.get(path).json()
        return result
    except RequestException as e:
        return None


def __get_user(user_id: str):
    path = f"https://localhost:8081/api/users/{user_id}"

    try:
        result: dict = requests.get(path).json()
        return result
    except RequestException as e:
        return None


def __update_user(user: dict):
    user_id = user['id']
    path = f"https://localhost:8081/api/users/{user_id}"

    try:
        result: dict = requests.post(path, json=user).json()
        return result
    except RequestException as e:
        return None


def __get_recipe(recipe_id: str):
    path = f"https://localhost:8082/api/recipes/{recipe_id}"

    try:
        result: dict = requests.get(path).json()
        return result
    except RequestException as e:
        return None


def __save_recipe(recipe: dict):
    recipe_id = recipe['id']
    path = f"https://localhost:8082/api/recipes/{recipe_id}"

    try:
        result: dict = requests.post(path, json=recipe).json()
        return result
    except RequestException as e:
        return None


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
    current_user_id = __get_current_user_id()
    recipe = __get_recipe(recipe_id)

    if not FavoriteRecipeInfoRepository.is_recipe_favorited_by(recipe_id, current_user_id):
        FavoriteRecipeInfoRepository.save(FavoriteRecipeInfo((recipe_id, current_user_id)))
        recipe["favoritesCount"] += 1
        __save_recipe(recipe)

    return jsonify(), 200


@bp.route('/api/recipes/<recipe_id>/favorite', methods=['DELETE'])
def unfavorite_recipe(recipe_id: str):
    current_user_id = __get_current_user_id()
    recipe = __get_recipe(recipe_id)

    if FavoriteRecipeInfoRepository.is_recipe_favorited_by(recipe_id, current_user_id):
        FavoriteRecipeInfoRepository.delete(FavoriteRecipeInfo((recipe_id, current_user_id)))
        recipe["favoritesCount"] -= 1
        __save_recipe(recipe)

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
    result = FollowInfoRepository.get_by_followed_id(user_id, page, limit)
    return [jsonify(__get_user(u.follower_id)) for u in result], 200


@bp.route('/api/users/<user_id>/follow', methods=['POST'])
def follow_user(user_id: str):
    current_user_id = __get_current_user_id()
    user = __get_user(user_id)

    if not FollowInfoRepository.is_followed_by(user_id, current_user_id):
        user["followersCount"] += 1
        __get_user(current_user_id)["followingCount"] += 1
        FollowInfoRepository.save(FollowInfo((user_id, current_user_id)))

    return jsonify({
        "following": True,
        "followersCount": user["followersCount"]
    }), 200


@bp.route('/api/users/<user_id>/follow', methods=['DELETE'])
def unfollow_user(user_id: str):
    current_user_id = __get_current_user_id()
    user = __get_user(user_id)

    if FollowInfoRepository.is_followed_by(user_id, current_user_id):
        user["followersCount"] -= 1
        __get_user(current_user_id)["followingCount"] -= 1
        FollowInfoRepository.delete(FollowInfo((user_id, current_user_id)))

    return jsonify({
        "following": False,
        "followersCount": user["followersCount"]
    }), 200

# notification service

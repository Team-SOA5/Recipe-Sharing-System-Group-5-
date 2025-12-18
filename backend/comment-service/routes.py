from flask import Blueprint, request, jsonify, g
from datetime import datetime
import pickle

from helpers import make_random_string
from repositories import *


bp = Blueprint('socials', __name__)


def __get_current_user_id() -> str | None:
    """
    Lấy user_id hiện tại.
    - Ưu tiên từ g.user_id (nếu sau này có middleware JWT).
    - Fallback từ query string: ?userId=...
    - Hoặc từ body JSON: { "userId": "..." }.
    """
    if getattr(g, 'user_id', None):
        return g.user_id

    user_id = request.args.get('userId') or request.args.get('user_id')
    if user_id:
        return user_id

    data = request.get_json(silent=True) or {}
    return data.get('userId') or data.get('user_id')


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
    # FE có thể không gửi images, default là danh sách rỗng
    images: list[str] = body.get('images', [])
    # Service này không có middleware JWT nên g.user_id thường là None.
    # Ưu tiên dùng user_id nếu gateway/Service khác set, fallback theo body hoặc anonymous.
    author_id: str = g.get('user_id') or body.get('authorId') or body.get('author') or 'anonymous'
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
    if not comment:
        return jsonify({'message': 'Comment not found'}), 404

    # Cập nhật nội dung nếu truyền lên
    if 'content' in body:
        comment.content = body['content']

    # Nếu FE không gửi author/images thì giữ nguyên giá trị cũ
    if 'author' in body:
        comment.author = body['author']
    if 'images' in body:
        comment.images = pickle.dumps(body['images'] or [])

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
    # FE hiện chỉ gửi rating, nên review là optional
    review: str = body.get('review', '')
    # Lấy authorId từ JWT (nếu có) hoặc từ body
    author_id: str = __get_current_user_id() or body.get('authorId') or body.get('author') or 'anonymous'
    created_at: datetime = datetime.now()
    # id sẽ là random string, recipe_id truyền riêng
    rating_id = make_random_string(16)
    result = Rating(rating_id, recipe_id, rating, review, author_id, created_at, created_at)
    RatingRepository.save(result)

    # Đồng bộ thống kê rating sang recipe-service (tăng count + update average)
    try:
        import requests

        recipe_service_url = 'http://localhost:8082'
        url = f"{recipe_service_url}/recipes/{recipe_id}/rating-stats"
        # oldRating = None vì đây là rating lần đầu
        requests.post(url, json={"rating": rating, "oldRating": None}, timeout=5)
    except Exception as e:
        print("WARN: failed to sync rating stats to recipe-service (create):", e)

    return jsonify(RatingRepository.get_by_author_id_and_recipe_id(author_id, recipe_id).to_dict()), 200


@bp.route('/api/recipes/<recipe_id>/ratings/me', methods=['GET'])
def get_my_ratings_of_recipe(recipe_id: str):
    user_id = __get_current_user_id()
    result = RatingRepository.get_by_author_id_and_recipe_id(user_id, recipe_id)
    if not result:
        # Chưa có rating nào của user cho recipe này
        return jsonify({}), 200
    return jsonify(result.to_dict()), 200


@bp.route('/api/recipes/<recipe_id>/ratings/me', methods=['PUT'])
def put_my_ratings_of_recipe(recipe_id: str):
    queries = request.args
    body = request.get_json()
    rating: int = body['rating']  # TODO: Constrain down to [1, 5]!
    # review optional
    review: str = body.get('review', '')
    author_id: str = __get_current_user_id() or body.get('authorId') or body.get('author') or 'anonymous'
    updated_at: datetime = datetime.now()
    existing = RatingRepository.get_by_author_id_and_recipe_id(author_id, recipe_id)
    old_rating_value = existing.rating if existing else None

    # Nếu chưa có rating trước đó, tạo mới luôn (giống POST)
    if not existing:
        rating_id = make_random_string(16)
        created_at: datetime = datetime.now()
        existing = Rating(rating_id, recipe_id, rating, review, author_id, created_at, updated_at)
    else:
        existing.rating = rating
        existing.review = review
        existing.updated_at = updated_at

    RatingRepository.save(existing)

    # Đồng bộ thống kê rating sang recipe-service
    try:
        import requests

        recipe_service_url = 'http://localhost:8082'
        url = f"{recipe_service_url}/recipes/{recipe_id}/rating-stats"
        requests.post(
            url,
            json={"rating": rating, "oldRating": old_rating_value},
            timeout=5,
        )
    except Exception as e:
        print("WARN: failed to sync rating stats to recipe-service (update):", e)

    return jsonify(existing.to_dict()), 200


@bp.route('/api/recipes/<recipe_id>/ratings/me', methods=['DELETE'])
def delete_my_ratings_of_recipe(recipe_id: str):
    author_id = __get_current_user_id()
    rating = RatingRepository.get_by_author_id_and_recipe_id(author_id, recipe_id)
    RatingRepository.delete(rating)
    return jsonify(), 200


# favorites service
@bp.route('/api/users/<user_id>/favorites', methods=['GET'])
def get_favorite_recipes_of_user(user_id: str):
    queries = request.args
    page: int = int(queries.get('page', 1))
    limit: int = int(queries.get('limit', 20))
    recipes = RecipeRepository.get_liked_recipes_of(user_id, page, limit)
    return jsonify([r.to_dict_for(user_id) for r in recipes]), 200


@bp.route('/api/favorites', methods=['GET'])
def get_favorite_recipes_of_me():
    return get_favorite_recipes_of_user(__get_current_user_id())


@bp.route('/api/recipes/<recipe_id>/favorite', methods=['POST'])
def favorite_recipe(recipe_id: str):
    body = request.get_json(silent=True) or {}
    # Ưu tiên user_id từ JWT (nếu sau này có), fallback theo body
    user_id = __get_current_user_id() or body.get('userId') or body.get('user_id')
    if not user_id:
        return jsonify({'message': 'Missing userId'}), 400

    recipe = RecipeRepository.get_by_id(recipe_id)
    if not recipe:
        # Nếu recipe chưa tồn tại trong social DB, tạo bản ghi rỗng chỉ để lưu trạng thái favorite
        # Các field khác có thể để trống / mặc định
        recipe = Recipe(
            id=recipe_id,
            title='',
            description='',
            thumbnail='',
            author='',
            category='',
            difficulty='easy',
            cooking_time=0,
            ratings_count=0,
            servings=0,
            average_ratings=0.0,
            rating_count=0,
            favorited_user_ids=[],
        )

    recipe.set_as_favorite_of(user_id)
    RecipeRepository.save(recipe)

    # Đồng bộ favoritesCount sang recipe-service
    try:
        import requests

        recipe_service_url = 'http://localhost:8082'  # recipe-service port
        url = f"{recipe_service_url}/recipes/{recipe_id}/favorite-count"
        requests.post(url, json={"delta": 1}, timeout=5)
    except Exception as e:
        print("WARN: failed to sync favoritesCount to recipe-service:", e)

    return jsonify(), 200


@bp.route('/api/recipes/<recipe_id>/favorite', methods=['DELETE'])
def unfavorite_recipe(recipe_id: str):
    body = request.get_json(silent=True) or {}
    user_id = __get_current_user_id() or body.get('userId') or body.get('user_id')
    if not user_id:
        return jsonify({'message': 'Missing userId'}), 400

    recipe = RecipeRepository.get_by_id(recipe_id)
    # Nếu chưa có bản ghi hoặc user chưa favorite thì coi như đã bỏ yêu thích (idempotent)
    if not recipe:
        return jsonify(), 204

    recipe.unset_as_favorite_of(user_id)
    RecipeRepository.save(recipe)

    # Đồng bộ favoritesCount sang recipe-service (giảm 1)
    try:
        import requests

        recipe_service_url = 'http://localhost:8082'  # recipe-service port
        url = f"{recipe_service_url}/recipes/{recipe_id}/favorite-count"
        requests.post(url, json={"delta": -1}, timeout=5)
    except Exception as e:
        print("WARN: failed to sync favoritesCount to recipe-service:", e)

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


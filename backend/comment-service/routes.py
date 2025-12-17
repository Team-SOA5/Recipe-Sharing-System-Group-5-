import pickle
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import Comment
from repositories import CommentRepository
from utils import make_random_string


bp = Blueprint('comment', __name__)


# @bp.route('/', methods=['GET'])
# def landing_page():
#     return 'Simply a landing page!'


@bp.route('/api/v1/recipes/<recipe_id>/comments', methods=['GET'])
def get_comments_of_recipe(recipe_id: str):
    queries = request.args
    page = int(queries.get('page', 1))
    limit = int(queries.get('limit', 20))
    sort = queries.get('sort', 'newest')
    comments = CommentRepository.get_comments_to_recipe(recipe_id, page, limit, sort)
    return jsonify([c.to_dict() for c in comments]), 200


@bp.route('/api/v1/recipes/<recipe_id>/comments', methods=['POST'])
def post_comment_of_recipe(recipe_id: str):
    queries = request.args
    body = request.get_json()
    content: str = body['content']
    images: list[str] = body['images']
    author = "" # TODO: find a way to get the active user!
    now = datetime.now()

    # TODO: str id generation + proper author value!
    comment = Comment(make_random_string(16), recipe_id, content, author, images,
                      0, False, now, now)

    CommentRepository.save_comment(comment)
    return jsonify(comment.to_dict()), 200


@bp.route('/api/v1/comments/<comment_id>', methods=['PUT'])
def update_comment(comment_id: str):
    queries = request.args
    body = request.get_json()
    comment = CommentRepository.get_comment_by_id(comment_id)
    comment.content = body['content']
    comment.author = body['author']
    comment.images = pickle.dumps(body['images'])
    comment.updated_at = datetime.now()
    CommentRepository.save_comment(comment)
    return jsonify(comment.to_dict()), 200


@bp.route('/api/v1/comments/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id: str):
    CommentRepository.delete_comment(CommentRepository.get_comment_by_id(comment_id))
    return jsonify(), 200


@bp.route('/api/v1/comments/<comment_id>/like', methods=['POST'])
def like_comment(comment_id: str):
    comment = CommentRepository.get_comment_by_id(comment_id)
    comment.is_liked = True
    comment.likes_count += 1
    CommentRepository.save_comment(comment)
    return jsonify({ "liked": True, "likesCount": comment.likes_count }), 200


@bp.route('/api/v1/comments/<comment_id>/like', methods=['DELETE'])
def unlike_comment(comment_id: str):
    comment = CommentRepository.get_comment_by_id(comment_id)
    comment.is_liked = False
    comment.likes_count -= 1
    CommentRepository.save_comment(comment)
    return jsonify({ "liked": False, "likesCount": comment.likes_count }), 200

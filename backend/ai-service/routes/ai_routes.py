from flask import Blueprint
from controllers.analyze_controller import trigger_analysis, chat_with_ai
from utils.jwt_service import jwt_required
from controllers.recommendation_controller import (
    get_recommendations, 
    get_detail, 
    delete_recommendation, 
    submit_feedback
)

ai_bp = Blueprint('ai', __name__)

# Analysis & Chat
@ai_bp.route('/ai/analyze', methods=['POST'])
@jwt_required
def analyze():
    return trigger_analysis()

@ai_bp.route('/ai/chat', methods=['POST'])
@jwt_required
def chat():
    return chat_with_ai()

# CRUD Recommendations
@ai_bp.route('/ai/recommendations', methods=['GET'])
@jwt_required
def list_recs():
    return get_recommendations()

@ai_bp.route('/ai/recommendations/<rec_id>', methods=['GET'])
@jwt_required
def detail_rec(rec_id):
    return get_detail(rec_id)

@ai_bp.route('/ai/recommendations/<rec_id>', methods=['DELETE'])
@jwt_required
def delete_rec(rec_id):
    return delete_recommendation(rec_id)

@ai_bp.route('/ai/recommendations/<rec_id>/feedback', methods=['POST'])
@jwt_required
def feedback_rec(rec_id):
    return submit_feedback(rec_id)
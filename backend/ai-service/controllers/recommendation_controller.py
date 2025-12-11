from flask import request, jsonify, g
from models.recommendation_model import RecommendationModel
from exceptions.exceptions import NotFoundError, ValidationError

# Khởi tạo Model
rec_model = RecommendationModel()

def get_recommendations():
    """
    Lấy danh sách các lần AI gợi ý (có phân trang, lọc theo hồ sơ bệnh án)
    GET /ai/recommendations
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        medical_record_id = request.args.get('medicalRecordId')
        
        # Gọi Model để lấy dữ liệu
        data, total = rec_model.find_all(g.user_id, page, limit, medical_record_id)
        
        return jsonify({
            "data": data,
            "pagination": {
                "currentPage": page,
                "totalItems": total,
                "totalPages": (total + limit - 1) // limit,
                "itemsPerPage": limit
            }
        }), 200
    except ValueError:
        raise ValidationError("Page and limit must be integers")

def get_detail(rec_id):
    """
    Lấy chi tiết một bản ghi Recommendation
    GET /ai/recommendations/<rec_id>
    """
    item = rec_model.find_by_id(rec_id, g.user_id)
    if not item:
        raise NotFoundError("Recommendation not found")
    
    return jsonify(item), 200

def delete_recommendation(rec_id):
    """
    Xóa lịch sử gợi ý
    DELETE /ai/recommendations/<rec_id>
    """
    success = rec_model.delete(rec_id, g.user_id)
    if success:
        return '', 204
    else:
        raise NotFoundError("Recommendation not found or could not be deleted")

def submit_feedback(rec_id):
    """
    Gửi feedback (rating, comment) cho kết quả AI
    POST /ai/recommendations/<rec_id>/feedback
    """
    data = request.json
    if not data or 'rating' not in data:
        raise ValidationError("Rating is required")
        
    # Validate rating range
    rating = data.get('rating')
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        raise ValidationError("Rating must be an integer between 1 and 5")

    success = rec_model.add_feedback(rec_id, g.user_id, data)
    
    if success:
        return jsonify({"message": "Cảm ơn feedback của bạn!"}), 200
    else:
        raise NotFoundError("Recommendation not found")
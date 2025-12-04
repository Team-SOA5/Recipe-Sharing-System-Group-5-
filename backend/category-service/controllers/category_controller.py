from flask import request, jsonify, g
from models.category_model import Category
from exceptions.exceptions import ErrorCode
from datetime import datetime

def _handle_error(e, code=500):
    return jsonify({"code": code, "message": str(e)}), code

# 1. Lấy danh sách (Public)
def get_categories():
    try:
        categories = Category.objects()
        return jsonify({
            "data": [c.to_json() for c in categories]
        }), 200
    except Exception as e:
        return _handle_error(e)

# 2. Tạo danh mục (Admin) - Cần Login
def create_category():
    try:
        data = request.json
        # Validate required fields theo openapi (chỉ có name là bắt buộc)
        if not data.get('name'):
            return jsonify({
                "code": ErrorCode.MISSING_FIELDS.code, 
                "message": "Thiếu thông tin bắt buộc: name"
            }), 400

        # Kiểm tra trùng tên
        if Category.objects(name=data['name']).first():
            return jsonify({"code": 400, "message": "Tên danh mục đã tồn tại"}), 400

        new_category = Category(
            name=data['name'],
            description=data.get('description'),
            icon=data.get('icon')
        )
        new_category.save()
        
        return jsonify(new_category.to_json()), 200 # 200 OK theo openapi
    except Exception as e:
        return _handle_error(e)

# 3. Lấy chi tiết danh mục (Public)
def get_category_detail(categoryId):
    try:
        category = Category.objects(id=categoryId).first()
        if not category:
            return jsonify({
                "code": ErrorCode.NOT_FOUND.code, 
                "message": ErrorCode.NOT_FOUND.message
            }), 404
        
        return jsonify(category.to_json()), 200
    except Exception as e:
        return _handle_error(e, 404) # Handle invalid ID format

# 4. Cập nhật (Admin) - Cần Login
def update_category(categoryId):
    try:
        category = Category.objects(id=categoryId).first()
        if not category:
            return jsonify({
                "code": ErrorCode.NOT_FOUND.code, 
                "message": ErrorCode.NOT_FOUND.message
            }), 404

        data = request.json
        if 'name' in data: 
            # Check duplicate name nếu đổi tên
            if data['name'] != category.name and Category.objects(name=data['name']).first():
                 return jsonify({"code": 400, "message": "Tên danh mục đã tồn tại"}), 400
            category.name = data['name']
            
        if 'description' in data: category.description = data['description']
        if 'icon' in data: category.icon = data['icon']
        
        category.updatedAt = datetime.utcnow()
        category.save()
        
        return jsonify(category.to_json()), 200
    except Exception as e:
        return _handle_error(e)

# 5. Xóa (Admin) - Cần Login
def delete_category(categoryId):
    try:
        category = Category.objects(id=categoryId).first()
        if not category:
            return jsonify({
                "code": ErrorCode.NOT_FOUND.code, 
                "message": ErrorCode.NOT_FOUND.message
            }), 404
            
        category.delete()
        return jsonify({"message": "Xóa thành công"}), 200
    except Exception as e:
        return _handle_error(e)
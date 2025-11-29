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
        if not data.get('name'):
            error = ErrorCode.MISSING_FIELDS
            return jsonify({"code": error.code, "message": error.message}), 400

        # Kiểm tra trùng tên
        if Category.objects(name=data['name']).first():
            error = ErrorCode.DUPLICATE_ENTRY
            return jsonify({"code": error.code, "message": "Danh mục đã tồn tại"}), 400

        new_category = Category(
            name=data['name'],
            description=data.get('description'),
            icon=data.get('icon')
        )
        new_category.save()
        
        return jsonify(new_category.to_json()), 200 
    except Exception as e:
        return _handle_error(e)

# 3. Lấy chi tiết danh mục (Public)
def get_category_detail(categoryId):
    try:
        category = Category.objects(id=categoryId).first()
        if not category:
            error = ErrorCode.NOT_FOUND
            return jsonify({"code": error.code, "message": error.message}), 404
        
        return jsonify(category.to_json()), 200
    except Exception as e:
        return _handle_error(e)

# 4. Cập nhật (Admin) - Cần Login
def update_category(categoryId):
    try:
        category = Category.objects(id=categoryId).first()
        if not category:
            error = ErrorCode.NOT_FOUND
            return jsonify({"code": error.code, "message": error.message}), 404

        data = request.json
        if 'name' in data: 
            # Check duplicate name nếu đổi tên
            if data['name'] != category.name and Category.objects(name=data['name']).first():
                 return jsonify({"code": 400, "message": "Tên danh mục đã tồn tại"}), 400
            category.name = data['name']
            
        if 'description' in data: category.description = data['description']
        if 'icon' in data: category.icon = data['icon']
        
        category.updated_at = datetime.utcnow()
        category.save()
        
        return jsonify(category.to_json()), 200
    except Exception as e:
        return _handle_error(e)

# 5. Xóa (Admin) - Cần Login
def delete_category(categoryId):
    try:
        category = Category.objects(id=categoryId).first()
        if not category:
            error = ErrorCode.NOT_FOUND
            return jsonify({"code": error.code, "message": error.message}), 404
            
        category.delete()
        return jsonify({"message": "Xóa thành công"}), 200
    except Exception as e:
        return _handle_error(e)
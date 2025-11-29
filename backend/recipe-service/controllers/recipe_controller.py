from flask import request, jsonify, g
from models.recipe_model import Recipe, Ingredient, Step
from exceptions.exceptions import ErrorCode
from datetime import datetime, timedelta
import mongoengine

def _handle_error(e, code=500):
    return jsonify({"code": code, "message": str(e)}), code

# 1. Lấy danh sách
def get_recipes():
    try:
        keyword = request.args.get('keyword')
        category_id = request.args.get('category_id')
        difficulty = request.args.get('difficulty')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        query = Recipe.objects()
        if keyword: query = query.filter(title__icontains=keyword)
        if category_id: query = query.filter(category_id=category_id)
        if difficulty: query = query.filter(difficulty=difficulty)

        total = query.count()
        recipes = query.skip((page - 1) * limit).limit(limit)

        return jsonify({
            "data": [r.to_json_summary() for r in recipes],
            "pagination": {"page": page, "limit": limit, "totalItems": total}
        }), 200
    except Exception as e:
        return _handle_error(e)

# 2. Tạo công thức
def create_recipe():
    try:
        data = request.json
        if not all(k in data for k in ('title', 'ingredients', 'steps')):
            error = ErrorCode.MISSING_FIELDS
            return jsonify({"code": error.code, "message": error.message}), 400

        ingredients = [Ingredient(**i) for i in data.get('ingredients', [])]
        steps = [Step(**s) for s in data.get('steps', [])]

        # Lấy calories từ input, mặc định là 0
        calories_input = data.get('calories', 0.0)

        recipe = Recipe(
            title=data['title'],
            description=data.get('description'),
            thumbnail=data.get('thumbnail'),
            ingredients=ingredients,
            steps=steps,
            difficulty=data.get('difficulty', 'Medium'),
            time_minutes=data.get('time_minutes', 0),
            serving=data.get('serving', 1),
            category_id=data.get('category_id'),
            tags=data.get('tags', []),
            author_id=g.user_id, # Lấy từ token
            calories=calories_input
        )
        recipe.save()
        return jsonify(recipe.to_json_detail()), 201
    except Exception as e:
        return _handle_error(e)

# 3. Xem chi tiết
def get_recipe_detail(id):
    try:
        recipe = Recipe.objects(id=id).first()
        if not recipe:
            error = ErrorCode.RECIPE_NOT_FOUND
            return jsonify({"code": error.code, "message": error.message}), 404
        return jsonify(recipe.to_json_detail()), 200
    except Exception as e:
        return _handle_error(e)

# 4. Cập nhật
def update_recipe(id):
    try:
        recipe = Recipe.objects(id=id).first()
        if not recipe:
            error = ErrorCode.RECIPE_NOT_FOUND
            return jsonify({"code": error.code, "message": error.message}), 404
        
        if recipe.author_id != g.user_id:
            error = ErrorCode.UNAUTHORIZED
            return jsonify({"code": error.code, "message": error.message}), 403

        data = request.json
        fields = ['title', 'description', 'thumbnail', 'difficulty', 'time_minutes', 'serving', 'category_id', 'tags', 'calories']
        for field in fields:
            if field in data: setattr(recipe, field, data[field])
        
        if 'ingredients' in data:
            recipe.ingredients = [Ingredient(**i) for i in data['ingredients']]
        if 'steps' in data:
            recipe.steps = [Step(**s) for s in data['steps']]
            
        recipe.updated_at = datetime.utcnow()
        recipe.save()
        return jsonify(recipe.to_json_detail()), 200
    except Exception as e:
        return _handle_error(e)

# 5. Xóa
def delete_recipe(id):
    try:
        recipe = Recipe.objects(id=id).first()
        if not recipe:
            error = ErrorCode.RECIPE_NOT_FOUND
            return jsonify({"code": error.code, "message": error.message}), 404
        
        if recipe.author_id != g.user_id:
            error = ErrorCode.UNAUTHORIZED
            return jsonify({"code": error.code, "message": error.message}), 403
            
        recipe.delete()
        return jsonify({"message": "Deleted"}), 200
    except Exception as e:
        return _handle_error(e)

# 6. Lấy theo User
def get_recipes_by_user(userId):
    try:
        recipes = Recipe.objects(author_id=userId)
        return jsonify({"data": [r.to_json_summary() for r in recipes]}), 200
    except Exception as e:
        return _handle_error(e)

#  7. Tăng lượt xem (/recipes/{id}/view)
def increment_view(id):
    try:
        recipe = Recipe.objects(id=id).first()
        if not recipe:
            error = ErrorCode.RECIPE_NOT_FOUND
            return jsonify({"code": error.code, "message": error.message}), 404
        
        # Tăng view atomic
        recipe.update(inc__views=1)
        recipe.reload() # Load lại để lấy số view mới
        
        return jsonify({"views": recipe.views}), 200
    except Exception as e:
        return _handle_error(e)

# Lấy Feed (/feed) - Tạm thời lấy recipe mới nhất
# (Cần tích hợp Follow Service để lấy list user_id mà user đang follow)
def get_feed():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Logic tạm: Lấy tất cả recipe mới nhất
        query = Recipe.objects().order_by('-created_at')
        
        total_items = query.count()
        total_pages = (total_items + limit - 1) // limit
        skip = (page - 1) * limit
        
        recipes = query.skip(skip).limit(limit)
        
        return jsonify({
            "data": [r.to_json_summary() for r in recipes],
            "pagination": {
                "page": page,
                "limit": limit,
                "totalItems": total_items,
                "totalPages": total_pages
            }
        }), 200
    except Exception as e:
        return _handle_error(e)


# 9. Lấy Trending (/trending/recipes)
def get_trending():
    try:
        limit = int(request.args.get('limit', 10))
        period = request.args.get('period', 'week') # day, week, month
        
        now = datetime.utcnow()
        start_date = now
        
        if period == 'day':
            start_date = now - timedelta(days=1)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else: # week
            start_date = now - timedelta(weeks=1)
            
        # Query: created_at >= start_date, order by views DESC
        recipes = Recipe.objects(created_at__gte=start_date).order_by('-views').limit(limit)
        
        return jsonify({
            "data": [r.to_json_summary() for r in recipes]
        }), 200
    except Exception as e:
        return _handle_error(e)
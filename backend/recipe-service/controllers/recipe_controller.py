from flask import request, jsonify, g
from models.recipe_model import Recipe, Ingredient, Instruction, NutritionInfo
from exceptions.exceptions import ErrorCode
from datetime import datetime, timedelta
import mongoengine
from mongoengine import Q
import logging

logger = logging.getLogger(__name__)

def _handle_error(e, code=500):
    logger.error(f"Error: {str(e)}") # Log lỗi ra để dễ debug
    return jsonify({"code": code, "message": str(e)}), code

# ... (giữ nguyên get_recipes) ...

# --- 1. Lấy danh sách (GET /recipes) ---
def get_recipes():
    try:
        categoryId = request.args.get('categoryId')
        sort = request.args.get('sort', 'newest')
        difficulty = request.args.get('difficulty')
        search_query = request.args.get('q')  # Thêm hỗ trợ search
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        query = Recipe.objects()
        if categoryId: query = query.filter(category_id=categoryId)
        if difficulty: query = query.filter(difficulty=difficulty)
        
        # Tìm kiếm theo title, description, ingredients
        if search_query:
            # MongoDB text search - tìm trong title, description, và name của ingredients
            query = query.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(ingredients__name__icontains=search_query)
            )

        # Sắp xếp
        if sort == 'newest': query = query.order_by('-createdAt')
        elif sort == 'oldest': query = query.order_by('createdAt')
        elif sort == 'most_viewed': query = query.order_by('-viewsCount')
        elif sort == 'most_liked': query = query.order_by('-favoritesCount')
        elif sort == 'relevance' and search_query:
            # Khi có search, sort theo relevance (giữ nguyên thứ tự MongoDB)
            pass  # MongoDB đã sort theo relevance khi dùng $regex
        
        total_items = query.count()
        total_pages = (total_items + limit - 1) // limit
        skip = (page - 1) * limit
        if skip < 0: skip = 0
        
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

# --- 2. Tạo công thức (POST /recipes) ---
def create_recipe():
    try:
        # Thêm try-except cho việc parse JSON để bắt lỗi định dạng JSON không hợp lệ
        try:
            data = request.get_json(force=True) # force=True giúp parse kể cả khi thiếu content-type header
        except Exception as e:
             return jsonify({
                "code": ErrorCode.BAD_REQUEST.code if hasattr(ErrorCode, 'BAD_REQUEST') else 400,
                "message": f"Invalid JSON format: {str(e)}"
            }), 400

        if not data:
             return jsonify({
                "code": ErrorCode.BAD_REQUEST.code if hasattr(ErrorCode, 'BAD_REQUEST') else 400, 
                "message": "No data provided"
            }), 400
        
        # Validate các trường bắt buộc cấp 1
        required_fields = ['title', 'ingredients', 'instructions']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return jsonify({
                "code": ErrorCode.MISSING_FIELDS.code, 
                "message": f"Thiếu thông tin bắt buộc: {', '.join(missing)}"
            }), 400

        # Parse Ingredients (Xử lý an toàn)
        ingredients_objs = []
        for i in data.get('ingredients', []):
            if isinstance(i, dict) and 'name' in i and 'amount' in i:
                ingredients_objs.append(Ingredient(
                    name=i['name'], 
                    amount=i['amount'], 
                    note=i.get('note', '')
                ))
        
        # Parse Instructions (Xử lý an toàn)
        instructions_objs = []
        for idx, s in enumerate(data.get('instructions', [])):
            if isinstance(s, dict) and 'description' in s:
                instructions_objs.append(Instruction(
                    step=s.get('step', idx + 1), 
                    description=s['description'], 
                    image=s.get('image', ''),
                    duration=s.get('duration', 0)
                ))

        # Parse Nutrition (Xử lý an toàn)
        nutri_data = data.get('nutritionInfo', {})
        if not isinstance(nutri_data, dict): nutri_data = {}
        
        nutrition_obj = NutritionInfo(
            calories=nutri_data.get('calories', 0),
            protein=nutri_data.get('protein', 0),
            carbs=nutri_data.get('carbs', 0),
            fat=nutri_data.get('fat', 0),
            fiber=nutri_data.get('fiber', 0)
        )

        # Lấy author_id từ JWT hoặc fallback
        author_id = getattr(g, 'user_id', None) or data.get('authorId') or data.get('author_id')
        if not author_id:
            return jsonify({
                "code": ErrorCode.UNAUTHENTICATED.code if hasattr(ErrorCode, 'UNAUTHENTICATED') else 401,
                "message": "Missing author_id. Please login or provide authorId in request body."
            }), 401

        # Convert cookingTime và servings sang int nếu là string
        cooking_time = data.get('cookingTime', 0)
        if isinstance(cooking_time, str):
            try:
                cooking_time = int(cooking_time)
            except:
                cooking_time = 0
        
        servings_count = data.get('servings', 1)
        if isinstance(servings_count, str):
            try:
                servings_count = int(servings_count)
            except:
                servings_count = 1

        new_recipe = Recipe(
            title=data['title'],
            description=data.get('description', ''),
            thumbnail=data.get('thumbnail', ''),
            author_id=author_id,
            category_id=data.get('categoryId', ''),
            difficulty=data.get('difficulty', 'medium'),
            cookingTime=cooking_time,
            servings=servings_count,
            ingredients=ingredients_objs,
            instructions=instructions_objs,
            images=data.get('images', []) if isinstance(data.get('images'), list) else [],
            tags=data.get('tags', []) if isinstance(data.get('tags'), list) else [],
            tips=data.get('tips', []) if isinstance(data.get('tips'), list) else [],
            nutritionInfo=nutrition_obj
        )
        
        new_recipe.save()
        return jsonify(new_recipe.to_json_detail()), 200

    except Exception as e:
        return _handle_error(e)

# --- 3. Xem chi tiết (GET /recipes/{id}) ---
def get_recipe_detail(recipeId):
    try:
        recipe = Recipe.objects(id=recipeId).first()
        if not recipe:
            return jsonify({"code": ErrorCode.RECIPE_NOT_FOUND.code, "message": ErrorCode.RECIPE_NOT_FOUND.message}), 404
        return jsonify(recipe.to_json_detail()), 200
    except Exception as e:
        return _handle_error(e, 404)

# --- 4. Cập nhật (PUT /recipes/{id}) ---
def update_recipe(recipeId):
    try:
        recipe = Recipe.objects(id=recipeId).first()
        if not recipe:
            return jsonify({"code": ErrorCode.RECIPE_NOT_FOUND.code, "message": ErrorCode.RECIPE_NOT_FOUND.message}), 404
        
        if recipe.author_id != g.user_id:
            return jsonify({"code": ErrorCode.UNAUTHORIZED.code, "message": ErrorCode.UNAUTHORIZED.message}), 403

        data = request.json
        
        # Cập nhật các trường đơn giản nếu có trong request
        simple_fields = ['title', 'description', 'thumbnail', 'categoryId', 'difficulty', 'cookingTime', 'servings', 'tags', 'tips', 'images']
        for field in simple_fields:
            if field in data: setattr(recipe, field, data[field])
            
        # Cập nhật Nested Fields (Replace toàn bộ list nếu có gửi lên)
        if 'ingredients' in data and isinstance(data['ingredients'], list):
            recipe.ingredients = [
                Ingredient(name=i['name'], amount=i['amount'], note=i.get('note', '')) 
                for i in data['ingredients'] if isinstance(i, dict) and 'name' in i and 'amount' in i
            ]
        
        if 'instructions' in data and isinstance(data['instructions'], list):
            recipe.instructions = [
                Instruction(step=s.get('step', idx+1), description=s['description'], image=s.get('image', ''), duration=s.get('duration', 0)) 
                for idx, s in enumerate(data['instructions']) if isinstance(s, dict) and 'description' in s
            ]
            
        if 'nutritionInfo' in data and isinstance(data['nutritionInfo'], dict):
            nutri = data['nutritionInfo']
            recipe.nutritionInfo = NutritionInfo(
                calories=nutri.get('calories', recipe.nutritionInfo.calories),
                protein=nutri.get('protein', recipe.nutritionInfo.protein),
                carbs=nutri.get('carbs', recipe.nutritionInfo.carbs),
                fat=nutri.get('fat', recipe.nutritionInfo.fat),
                fiber=nutri.get('fiber', recipe.nutritionInfo.fiber)
            )
            
        recipe.updatedAt = datetime.utcnow()
        recipe.save()
        return jsonify(recipe.to_json_detail()), 200
    except Exception as e:
        return _handle_error(e)

# --- 5. Xóa (DELETE /recipes/{id}) ---
def delete_recipe(recipeId):
    try:
        recipe = Recipe.objects(id=recipeId).first()
        if not recipe:
            return jsonify({"code": ErrorCode.RECIPE_NOT_FOUND.code, "message": ErrorCode.RECIPE_NOT_FOUND.message}), 404
        
        if recipe.author_id != g.user_id:
            return jsonify({"code": ErrorCode.UNAUTHORIZED.code, "message": ErrorCode.UNAUTHORIZED.message}), 403
            
        recipe.delete()
        return jsonify({"message": "Deleted"}), 200
    except Exception as e:
        return _handle_error(e)

# --- 6. Tăng view (POST /recipes/{id}/view) ---
def increment_view(recipeId):
    try:
        recipe = Recipe.objects(id=recipeId).first()
        if not recipe:
            return jsonify({"code": 404, "message": "Not Found"}), 404
        
        recipe.update(inc__viewsCount=1)
        recipe.reload()
        return jsonify({"views": recipe.viewsCount}), 200
    except Exception as e:
        return _handle_error(e)


# --- 6b. Internal: cập nhật favoritesCount (POST /recipes/{id}/favorite-count) ---
def update_favorite_count(recipeId):
    """
    Internal endpoint cho comment-service gọi để đồng bộ favoritesCount.
    Body: { "delta": 1 } hoặc { "delta": -1 }
    """
    try:
        data = request.get_json(silent=True) or {}
        delta = int(data.get('delta', 0))
        if delta == 0:
            return jsonify({"message": "delta must be non-zero"}), 400

        recipe = Recipe.objects(id=recipeId).first()
        if not recipe:
            return jsonify({"code": 404, "message": "Not Found"}), 404

        new_value = max(0, recipe.favoritesCount + delta)
        recipe.update(set__favoritesCount=new_value)
        recipe.reload()
        return jsonify({"favoritesCount": recipe.favoritesCount}), 200
    except Exception as e:
        return _handle_error(e)


# --- 6c. Internal: cập nhật thống kê rating (POST /recipes/{id}/rating-stats) ---
def update_rating_stats(recipeId):
    try:
        data = request.get_json(silent=True) or {}
        if "rating" not in data:
            return jsonify({"message": "rating is required"}), 400

        new_rating = float(data["rating"])
        old_rating = data.get("oldRating")
        old_rating = float(old_rating) if old_rating is not None else None

        recipe = Recipe.objects(id=recipeId).first()
        if not recipe:
            return jsonify({"code": 404, "message": "Not Found"}), 404

        current_avg = recipe.averageRating or 0.0
        current_count = recipe.ratingsCount or 0

        if old_rating is None:
            # Rating lần đầu: tăng count
            new_count = current_count + 1
            if new_count <= 0:
                new_count = 1
            new_avg = (current_avg * current_count + new_rating) / new_count
        else:
            # Update rating: giữ nguyên count, thay điểm cũ bằng mới
            new_count = max(current_count, 1)
            new_avg = (current_avg * new_count - old_rating + new_rating) / new_count

        recipe.update(set__averageRating=new_avg, set__ratingsCount=new_count)
        recipe.reload()
        return jsonify(
            {
                "averageRating": recipe.averageRating,
                "ratingsCount": recipe.ratingsCount,
            }
        ), 200
    except Exception as e:
        return _handle_error(e)

# --- 7. Feed (GET /feed) ---
def get_feed():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        query = Recipe.objects().order_by('-createdAt')
        total = query.count()
        recipes = query.skip((page-1)*limit).limit(limit)
        
        return jsonify({
            "data": [r.to_json_summary() for r in recipes],
            "pagination": {"page": page, "limit": limit, "totalItems": total}
        }), 200
    except Exception as e:
        return _handle_error(e)

# --- 8. Trending (GET /trending/recipes) ---
def get_trending():
    try:
        limit = int(request.args.get('limit', 10))
        period = request.args.get('period', 'week')
        
        now = datetime.utcnow()
        if period == 'day': start_date = now - timedelta(days=1)
        elif period == 'month': start_date = now - timedelta(days=30)
        else: start_date = now - timedelta(weeks=1)
        
        recipes = Recipe.objects(createdAt__gte=start_date).order_by('-viewsCount').limit(limit)
        return jsonify({"data": [r.to_json_summary() for r in recipes]}), 200
    except Exception as e:
        return _handle_error(e)

# --- 9. Lấy công thức của User (GET /users/{userId}/recipes) ---
def get_recipes_by_user(userId):
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        sort = request.args.get('sort', 'newest')
        
        # Query recipes by author_id
        query = Recipe.objects(author_id=userId)
        
        # Sort
        if sort == 'newest':
            query = query.order_by('-createdAt')
        elif sort == 'oldest':
            query = query.order_by('createdAt')
        elif sort == 'most_viewed':
            query = query.order_by('-viewsCount')
        elif sort == 'most_liked':
            query = query.order_by('-favoritesCount')
        
        # Pagination
        total_items = query.count()
        total_pages = (total_items + limit - 1) // limit
        skip = (page - 1) * limit
        if skip < 0:
            skip = 0
        
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
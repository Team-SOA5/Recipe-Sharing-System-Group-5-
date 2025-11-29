from flask import Blueprint
from controllers import recipe_controller
# [QUAN TRỌNG] Import đúng tên hàm jwt_required từ file của bạn
from utils.jwt_service import jwt_required

recipe_bp = Blueprint('recipe_bp', __name__)

# --- Public Routes (Không cần Token) ---
# 1. Lấy danh sách (có search, filter)
recipe_bp.route('/', methods=['GET'])(recipe_controller.get_recipes)

# 2. Lấy chi tiết
recipe_bp.route('/<id>', methods=['GET'])(recipe_controller.get_recipe_detail)

# 3. Lấy danh sách của user cụ thể
recipe_bp.route('/user/<userId>', methods=['GET'])(recipe_controller.get_recipes_by_user)

# 4. Tăng view
recipe_bp.route('/<id>/view', methods=['POST'])(recipe_controller.increment_view)

# 5. Lấy trending recipes
recipe_bp.route('/trending/recipes', methods=['GET'])(recipe_controller.get_trending)


# --- Protected Routes (Cần Token - dùng @jwt_required) ---
# 6. Tạo công thức mới
recipe_bp.route('/', methods=['POST'])(jwt_required(recipe_controller.create_recipe))

# 7. Cập nhật công thức
recipe_bp.route('/<id>', methods=['PUT'])(jwt_required(recipe_controller.update_recipe))

# 8. Xóa công thức
recipe_bp.route('/<id>', methods=['DELETE'])(jwt_required(recipe_controller.delete_recipe))

# 9. Lấy feed (cá nhân hóa)
recipe_bp.route('/feed', methods=['GET'])(jwt_required(recipe_controller.get_feed))
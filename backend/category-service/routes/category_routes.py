from flask import Blueprint
from controllers import category_controller
from utils.jwt_service import jwt_required

category_bp = Blueprint('category_bp', __name__)

# --- Public Routes ---
category_bp.route('/', methods=['GET'])(category_controller.get_categories)
category_bp.route('/<categoryId>', methods=['GET'])(category_controller.get_category_detail)

# --- Protected Routes (Admin) ---
# Ở đây dùng jwt_required để đảm bảo có token. 
# Việc check role 'admin' nên được thực hiện thêm trong middleware hoặc controller nếu cần chặt chẽ hơn.
category_bp.route('/', methods=['POST'])(jwt_required(category_controller.create_category))
category_bp.route('/<categoryId>', methods=['PUT'])(jwt_required(category_controller.update_category))
category_bp.route('/<categoryId>', methods=['DELETE'])(jwt_required(category_controller.delete_category))
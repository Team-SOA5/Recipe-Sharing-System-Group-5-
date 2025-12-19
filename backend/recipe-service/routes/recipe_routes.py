from flask import Blueprint
from controllers import recipe_controller
from utils.jwt_service import jwt_required

recipe_bp = Blueprint('recipe_bp', __name__)

# --- Public Routes ---
recipe_bp.route('', methods=['GET'])(recipe_controller.get_recipes) # /recipes
recipe_bp.route('/<recipeId>', methods=['GET'])(recipe_controller.get_recipe_detail)
recipe_bp.route('/<recipeId>/view', methods=['POST'])(recipe_controller.increment_view)
recipe_bp.route('/<recipeId>/favorite-count', methods=['POST'])(recipe_controller.update_favorite_count)
recipe_bp.route('/trending/recipes', methods=['GET'])(recipe_controller.get_trending)

# --- Internal Routes (No auth required, for seed data) ---
recipe_bp.route('/internal', methods=['POST'])(recipe_controller.create_recipe_internal)

# --- Protected Routes ---
recipe_bp.route('', methods=['POST'])(jwt_required(recipe_controller.create_recipe))
recipe_bp.route('/<recipeId>', methods=['PUT'])(jwt_required(recipe_controller.update_recipe))
recipe_bp.route('/<recipeId>', methods=['DELETE'])(jwt_required(recipe_controller.delete_recipe))
recipe_bp.route('/feed', methods=['GET'])(jwt_required(recipe_controller.get_feed))
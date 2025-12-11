from flask import jsonify
from exceptions.exceptions import AppError, ErrorCode  # <-- Sửa thành AppError

def register_error_handlers(app):
    @app.errorhandler(AppError)  # <-- Sửa thành AppError
    def handle_app_error(e):
        return jsonify({
            "code": e.error_code.code,
            "message": e.message
        }), e.error_code.http_status.value

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "code": ErrorCode.INVALID_REQUEST.code,
            "message": "Endpoint not found"
        }), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "code": ErrorCode.UNKNOWN_ERROR.code,
            "message": str(e)
        }), 500
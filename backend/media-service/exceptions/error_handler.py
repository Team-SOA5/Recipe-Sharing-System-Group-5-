from flask import jsonify
from exceptions.exceptions import AppException, ErrorCode
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """
    Đăng ký các error handlers cho Flask app
    """
    
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        """
        Handler cho AppException
        """
        error_code = error.error_code
        response = {
            'code': error_code.code,
            'message': error_code.message
        }
        return jsonify(response), error_code.http_status
    
    @app.errorhandler(Exception)
    def handle_runtime_exception(error):
        """
        Handler cho RuntimeException và các exception chưa được xử lý
        """
        # Nếu là HTTP exception từ Flask, giữ nguyên status code
        if isinstance(error, HTTPException):
            return jsonify({
                'code': error.code,
                'message': error.description
            }), error.code
        
        # Các exception khác trả về UNCATEGORIZED
        error_code = ErrorCode.UNCATEGORIZED
        response = {
            'code': error_code.code,
            'message': error_code.message
        }
        return jsonify(response), error_code.http_status
    
    @app.errorhandler(PermissionError)
    def handle_access_denied_exception(error):
        """
        Handler cho PermissionError
        """
        error_code = ErrorCode.UNAUTHORIZED
        response = {
            'code': error_code.code,
            'message': error_code.message
        }
        return jsonify(response), error_code.http_status

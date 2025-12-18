from flask import jsonify
from werkzeug.exceptions import HTTPException
from exceptions.exceptions import AppException, ErrorCode


def register_error_handlers(app):
    """
    Register error handlers for the Flask application
    Equivalent to GlobalException.java @ControllerAdvice
    """
    
    @app.errorhandler(AppException)
    def handle_app_exception(error: AppException):
        """Handle custom application exceptions"""
        error_code = error.get_error_code()
        response = {
            'code': error_code.code,
            'message': error_code.message
        }
        return jsonify(response), error_code.http_status.value
    
    @app.errorhandler(RuntimeError)
    def handle_runtime_exception(error: RuntimeError):
        """Handle runtime exceptions"""
        error_code = ErrorCode.UNCATEGORIZED
        response = {
            'code': error_code.code,
            'message': error_code.message
        }
        return jsonify(response), error_code.http_status.value
    
    @app.errorhandler(PermissionError)
    def handle_access_denied_exception(error: PermissionError):
        """Handle access denied exceptions"""
        error_code = ErrorCode.UNAUTHORIZED
        response = {
            'code': error_code.code,
            'message': error_code.message
        }
        return jsonify(response), error_code.http_status.value
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle HTTP exceptions"""
        response = {
            'code': error.code,
            'message': error.description
        }
        return jsonify(response), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        """Handle all other exceptions"""
        error_code = ErrorCode.UNCATEGORIZED
        response = {
            'code': error_code.code,
            'message': str(error) if app.debug else error_code.message
        }
        return jsonify(response), error_code.http_status.value

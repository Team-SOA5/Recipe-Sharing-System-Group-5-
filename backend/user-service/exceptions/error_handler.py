from flask import jsonify
from werkzeug.exceptions import HTTPException
from exceptions.exceptions import AppException, ErrorCode
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register error handlers for the Flask application"""
    
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        """Handle custom AppException"""
        logger.error(f"AppException: {error.error_code.message}")
        response = {
            'code': error.error_code.code,
            'message': error.error_code.message
        }
        return jsonify(response), error.error_code.http_status.value
    
    @app.errorhandler(Exception)
    def handle_runtime_exception(error):
        """Handle general runtime exceptions"""
        logger.error(f"RuntimeException: {str(error)}", exc_info=True)
        error_code = ErrorCode.UNCATEGORIZED
        response = {
            'code': error_code.code,
            'message': error_code.message
        }
        return jsonify(response), error_code.http_status.value
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle HTTP exceptions"""
        logger.error(f"HTTPException: {error.description}")
        response = {
            'code': error.code,
            'message': error.description
        }
        return jsonify(response), error.code
    
    @app.errorhandler(403)
    def handle_access_denied(error):
        """Handle access denied (403)"""
        error_code = ErrorCode.UNAUTHORIZED
        response = {
            'code': error_code.code,
            'message': error_code.message
        }
        return jsonify(response), error_code.http_status.value
    
    @app.errorhandler(401)
    def handle_unauthenticated(error):
        """Handle unauthenticated (401)"""
        error_code = ErrorCode.UNAUTHENTICATED
        response = {
            'code': error_code.code,
            'message': error_code.message
        }
        return jsonify(response), error_code.http_status.value

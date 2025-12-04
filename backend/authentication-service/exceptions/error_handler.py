from flask import jsonify
from exceptions.exceptions import AppException, ErrorCode
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register global error handlers - equivalent to Java GlobalException"""
    
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        """Handle application exceptions"""
        error_code = error.error_code
        return jsonify({
            'code': error_code.code,
            'message': error_code.message,
            'data': None
        }), error_code.http_status.value
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle database integrity errors"""
        logger.error(f"Integrity error: {str(error)}")
        error_code = ErrorCode.USER_EXISTED
        return jsonify({
            'code': error_code.code,
            'message': error_code.message,
            'data': None
        }), error_code.http_status.value
    
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """Handle validation errors"""
        logger.error(f"Validation error: {str(error)}")
        error_code = ErrorCode.INVALID_KEY
        return jsonify({
            'code': error_code.code,
            'message': str(error),
            'data': None
        }), error_code.http_status.value
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all other exceptions"""
        logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        error_code = ErrorCode.UNCATEGORIZED
        return jsonify({
            'code': error_code.code,
            'message': error_code.message,
            'data': None
        }), error_code.http_status.value

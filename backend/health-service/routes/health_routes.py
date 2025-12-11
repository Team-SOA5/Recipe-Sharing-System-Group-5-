from flask import Blueprint
from controllers.medical_record_controller import (
    get_medical_records, upload_medical_record, 
    get_medical_record_detail, delete_medical_record,
    update_record_from_ai,
    reprocess_medical_record
)
from utils.jwt_service import jwt_required

health_bp = Blueprint('health', __name__)

# Public APIs
@health_bp.route('/health/medical-records', methods=['GET'])
@jwt_required
def list_route(): return get_medical_records()

@health_bp.route('/health/medical-records', methods=['POST'])
@jwt_required
def upload_route(): return upload_medical_record()

@health_bp.route('/health/medical-records/<record_id>', methods=['GET'])
@jwt_required
def detail_route(record_id): return get_medical_record_detail(record_id)

@health_bp.route('/health/medical-records/<record_id>', methods=['DELETE'])
@jwt_required
def delete_route(record_id): return delete_medical_record(record_id)

# Internal API (Callback) - Có thể bảo vệ bằng IP Whitelist hoặc Internal Key
@health_bp.route('/health/internal/medical-records/<record_id>/update', methods=['PUT'])
def internal_update_route(record_id):
    return update_record_from_ai(record_id)

@health_bp.route('/health/medical-records/<record_id>/reprocess', methods=['POST'])
@jwt_required
def reprocess_route(record_id):
    return reprocess_medical_record(record_id)
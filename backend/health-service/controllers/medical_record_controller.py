import os
import requests
import threading
from flask import request, jsonify, g
from werkzeug.utils import secure_filename
from models.medical_record_model import MedicalRecordModel
from exceptions.exceptions import ValidationError, NotFoundError, AppError, ErrorCode

record_model = MedicalRecordModel()
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'heic'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- HELPER: GỌI SERVICE KHÁC ---
def upload_to_media_service(file, token):
    """Upload file sang Media Service"""
    media_url = os.getenv('MEDIA_SERVICE_URL')
    try:
        # Reset file pointer
        file.stream.seek(0)
        files = {'file': (file.filename, file.stream, file.content_type)}
        headers = {'Authorization': token}
        
        # Gọi API Upload của Media Service
        resp = requests.post(f"{media_url}/upload", files=files, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json().get('url')
        else:
            raise AppError(ErrorCode.UNKNOWN_ERROR, f"Media Upload Failed: {resp.text}")
    except Exception as e:
        print(f"Media Service Error: {e}")
        raise AppError(ErrorCode.UNKNOWN_ERROR, "Cannot connect to Media Service")

def trigger_ai_analysis(record_id, token):
    """Gửi tín hiệu sang AI Service để bắt đầu phân tích"""
    ai_url = os.getenv('AI_SERVICE_URL')
    try:
        headers = {'Authorization': token}
        payload = {
            "medicalRecordId": record_id,
            "options": {"mode": "full_analysis"} 
        }
        # Fire and Forget (Không chờ kết quả)
        requests.post(f"{ai_url}/analyze", json=payload, headers=headers, timeout=5)
    except Exception as e:
        print(f"Trigger AI Error: {e}")

# --- API HANDLERS ---

def upload_medical_record():
    if 'file' not in request.files:
        raise ValidationError("No file part")
    
    file = request.files['file']
    title = request.form.get('title', 'Untitled')
    notes = request.form.get('notes', '')
    
    if not allowed_file(file.filename):
        raise ValidationError("File type not allowed")
    
    # 1. Upload sang Media Service
    token = request.headers.get('Authorization')
    file_url = upload_to_media_service(file, token)
    
    # 2. Lưu Metadata vào DB (Status = Pending)
    record_data = {
        "userId": g.user_id,
        "title": title,
        "notes": notes,
        "fileUrl": file_url,
        "status": "pending"
    }
    record_id = record_model.create(record_data)
    
    # 3. Trigger AI Service (Chạy ngầm)
    thread = threading.Thread(target=trigger_ai_analysis, args=(record_id, token))
    thread.start()
    
    new_record = record_model.find_by_id(record_id, g.user_id)
    return jsonify({
        "message": "Upload thành công. Đang gửi sang AI xử lý...",
        "medicalRecord": new_record
    }), 201

def get_medical_records():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    status = request.args.get('status')
    records, total = record_model.find_all(g.user_id, page, limit, status)
    return jsonify({
        "data": records,
        "pagination": {"currentPage": page, "totalItems": total, "totalPages": (total + limit - 1) // limit}
    }), 200

def get_medical_record_detail(record_id):
    record = record_model.find_by_id(record_id, g.user_id)
    if not record: raise NotFoundError()
    return jsonify(record), 200

def delete_medical_record(record_id):
    if record_model.delete(record_id, g.user_id):
        return '', 204
    raise NotFoundError()

# --- INTERNAL CALLBACK (AI GỌI VỀ) ---
def update_record_from_ai(record_id):
    """AI Service gọi API này để update dữ liệu trích xuất được"""
    data = request.json
    status = data.get('status')
    
    if status == 'failed':
        record_model.update_status_and_data(
            record_id, status='failed', error_msg=data.get('errorMessage')
        )
    else:
        record_model.update_status_and_data(
            record_id, 
            status='processed',
            extracted_text=data.get('extractedText'),
            extracted_data=data.get('extractedData')
        )
    return jsonify({"message": "Updated"}), 200

def reprocess_medical_record(record_id):
    """
    POST /health/medical-records/{recordId}/reprocess
    Chạy lại quá trình phân tích và AI recommendation
    """
    # 1. Kiểm tra tồn tại
    record = record_model.find_by_id(record_id, g.user_id)
    if not record:
        raise NotFoundError("Medical record not found")
    
    # 2. Cập nhật trạng thái về processing
    # Reset lại các trường extracted để đảm bảo sạch sẽ
    record_model.update_status_and_data(
        record_id, 
        status='processing',
        extracted_text="",
        extracted_data={},
        error_msg=None
    )
    
    # 3. Trigger lại AI Service
    # Lưu ý: Cần lấy token từ header hiện tại để forward sang AI
    token = request.headers.get('Authorization')
    thread = threading.Thread(target=trigger_ai_analysis, args=(record_id, token))
    thread.start()
    
    # 4. Trả về kết quả ngay (như mô tả YAML trả về 200 kèm message)
    updated_record = record_model.find_by_id(record_id, g.user_id)
    
    return jsonify({
        "message": "Đang xử lý lại hồ sơ...",
        "medicalRecord": updated_record
    }), 200
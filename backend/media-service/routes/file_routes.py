from flask import Blueprint, request, send_file, jsonify, g
import io

# Import các thành phần trong dự án
from services.file_service import FileService
from repositories.file_management_repository import FileManagementRepository
from repositories.file_repository import FileRepository
from utils.jwt_service import jwt_required  # Dùng jwt_required thay vì token_required
from config import app_config

# Khởi tạo Blueprint
# Lưu ý: Không cần url_prefix="/media" ở đây nếu trong app.py đã register với prefix đó rồi
file_bp = Blueprint('file', __name__)

# Khởi tạo Repositories & Service
# (Repository tự lấy config từ app_config bên trong nó, không cần truyền tham số)
file_management_repository = FileManagementRepository()
file_repository = FileRepository()

file_service = FileService() 
# Lưu ý: FileService tôi viết trước đó tự khởi tạo repo bên trong __init__
# Nếu bạn muốn Dependency Injection như code của bạn, 
# bạn cần sửa lại FileService __init__ để nhận tham số. 
# Nhưng để chạy ngay với code cũ, ta dùng: file_service = FileService()

@file_bp.route('/download/<file_name>', methods=['GET'])
@jwt_required
def download(file_name):
    """
    URL: GET /media/download/{fileName}
    """
    # Gọi đúng tên hàm trong Service: get_file_for_download
    file_path, original_name = file_service.get_file_for_download(file_name)
    
    # Trả về file trực tiếp từ ổ cứng
    return send_file(
        file_path,
        download_name=original_name,
        as_attachment=True
    )

@file_bp.route('/upload', methods=['POST'])
@jwt_required
def upload():
    """
    URL: POST /media/upload
    """
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'code': 400, 'message': 'No file selected'}), 400
    
    # Gọi đúng hàm upload_file và truyền user_id lấy từ token (g.user_id)
    response = file_service.upload_file(file, g.user_id)
    
    return jsonify(response), 200

@file_bp.route('/batch-upload', methods=['POST'])
@jwt_required
def batch_upload():
    """
    URL: POST /media/batch-upload
    """
    if 'files' not in request.files:
        return jsonify({'code': 400, 'message': 'No files part'}), 400
    
    files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return jsonify({'code': 400, 'message': 'No files selected'}), 400
    
    # Gọi đúng hàm batch_upload và truyền user_id
    response = file_service.batch_upload(files, g.user_id)
    
    return jsonify(response), 200
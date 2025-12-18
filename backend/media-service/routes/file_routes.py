from flask import Blueprint, request, send_file, jsonify
from services.file_service import FileService
from repositories.file_management_repository import FileManagementRepository
from repositories.file_repository import FileRepository
from utils.jwt_service import token_required
from config import Config
import io


# Khởi tạo Blueprint cho file routes
file_bp = Blueprint('file', __name__, url_prefix="/media")


# Khởi tạo repositories và service
file_management_repository = FileManagementRepository()
file_repository = FileRepository(
    storage_dir=Config.FILE_STORAGE_DIR,
    url_prefix=Config.FILE_DOWNLOAD_PREFIX
)
file_service = FileService(file_management_repository, file_repository)


@file_bp.route('/download/<file_name>', methods=['GET'])
def download(file_name):
    """
    Endpoint để download file
    
    
    URL: GET /download/{fileName}
    """
    file_data = file_service.download(file_name)
    
    # Tạo BytesIO object từ file content
    return send_file(
        io.BytesIO(file_data.resource),
        mimetype=file_data.content_type,
        as_attachment=False
    )


@file_bp.route('/upload', methods=['POST'])
@token_required
def upload():
    """
    Endpoint để upload single file
    
    
    URL: POST /upload
    Form data: file (MultipartFile)
    """
    if 'file' not in request.files:
        return jsonify({
            'code': 400,
            'message': 'No file part in the request'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'code': 400,
            'message': 'No file selected'
        }), 400
    
    file_response = file_service.upload(file)
    return jsonify(file_response.to_dict()), 200


@file_bp.route('/batch-upload', methods=['POST'])
@token_required
def batch_upload():
    """
    Endpoint để upload multiple files
    
    
    URL: POST /batch-upload
    Form data: files (List<MultipartFile>)
    """
    if 'files' not in request.files:
        return jsonify({
            'code': 400,
            'message': 'No files part in the request'
        }), 400
    
    files = request.files.getlist('files')
    
    if not files or all(f.filename == '' for f in files):
        return jsonify({
            'code': 400,
            'message': 'No files selected'
        }), 400
    
    batch_response = file_service.batch_upload(files)
    return jsonify(batch_response.to_dict()), 200

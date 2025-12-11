import uuid
import os
from werkzeug.utils import secure_filename
from repositories.file_management_repository import FileManagementRepository
from repositories.file_repository import FileRepository
from config import app_config
# --- QUAN TRỌNG: Import AppError (không phải AppException) ---
from exceptions.exceptions import AppError, ErrorCode 

class FileService:
    def __init__(self):
        self.meta_repo = FileManagementRepository()
        self.storage_repo = FileRepository()

    def upload_file(self, file, user_id):
        if not file:
            raise AppError(ErrorCode.NO_FILE_UPLOADED)

        original_filename = secure_filename(file.filename)
        # Tạo tên file unique
        ext = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{ext}"

        # 1. Lưu file vật lý
        self.storage_repo.save_file(file, unique_filename)

        # 2. Lưu metadata vào DB
        file_meta = {
            "fileName": unique_filename,
            "originalFileName": original_filename,
            "contentType": file.content_type,
            "size": 0, 
            "userId": user_id,
            "uploadType": "SINGLE"
        }
        self.meta_repo.save(file_meta)

        # 3. Tạo response
        full_url = f"{app_config.download_prefix}{unique_filename}"
        
        return {
            "originalFileName": original_filename,
            "url": full_url
        }

    def batch_upload(self, files, user_id):
        if not files:
            raise AppError(ErrorCode.NO_FILE_UPLOADED)
        
        results = []
        for file in files:
            if file.filename == '':
                continue
            
            original_filename = secure_filename(file.filename)
            ext = os.path.splitext(original_filename)[1]
            unique_filename = f"{uuid.uuid4()}{ext}"

            self.storage_repo.save_file(file, unique_filename)

            file_meta = {
                "fileName": unique_filename,
                "originalFileName": original_filename,
                "contentType": file.content_type,
                "userId": user_id,
                "uploadType": "BATCH"
            }
            self.meta_repo.save(file_meta)
            
            results.append({
                "url": f"{app_config.download_prefix}{unique_filename}"
            })

        return {"uploads": results}

    def get_file_for_download(self, filename):
        meta = self.meta_repo.find_by_filename(filename)
        if not meta:
            raise AppError(ErrorCode.FILE_NOT_FOUND)
            
        path = self.storage_repo.get_file_path(filename)
        return path, meta.get('originalFileName')
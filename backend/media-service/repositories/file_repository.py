import os
from config import app_config  # Import config instance
from exceptions.exceptions import AppError, ErrorCode

class FileRepository:
    def __init__(self):
        # Tự động lấy đường dẫn lưu trữ từ config
        self.storage_dir = app_config.storage_dir

    def save_file(self, file_storage, filename):
        try:
            # Tạo đường dẫn đầy đủ
            save_path = os.path.join(self.storage_dir, filename)
            
            # Đảm bảo thư mục tồn tại
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Lưu file
            file_storage.save(save_path)
            return save_path
        except Exception as e:
            print(f"File Save Error: {e}")
            raise AppError(ErrorCode.FILE_SAVE_ERROR, str(e))

    def get_file_path(self, filename):
        path = os.path.join(self.storage_dir, filename)
        if not os.path.exists(path):
            raise AppError(ErrorCode.FILE_NOT_FOUND)
        return path
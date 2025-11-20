import os
import uuid
import hashlib
from pathlib import Path
from werkzeug.utils import secure_filename
from dto.requests import FileInfo
from models.models import FileManagement


class FileRepository:
    """
    Repository xử lý file storage - tương ứng với FileRepository trong Java
    Quản lý việc lưu trữ và đọc file từ filesystem
    """
    
    def __init__(self, storage_dir, url_prefix):
        """
        Args:
            storage_dir: Thư mục lưu trữ file (từ config)
            url_prefix: URL prefix để tạo download URL (từ config)
        """
        self.storage_dir = storage_dir
        self.url_prefix = url_prefix
    
    def save(self, file):
        """
        Lưu file vào filesystem
        
        Args:
            file: FileStorage object từ Flask request
            
        Returns:
            FileInfo object chứa thông tin file đã lưu
        """
        # Tạo thư mục nếu chưa tồn tại
        folder = Path(self.storage_dir).resolve()
        folder.mkdir(parents=True, exist_ok=True)
        
        # Lấy extension của file
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1] if original_filename else ''
        
        # Tạo tên file unique bằng UUID
        if file_extension:
            file_name = f"{uuid.uuid4()}{file_extension}"
        else:
            file_name = str(uuid.uuid4())
        
        # Đường dẫn đầy đủ để lưu file
        file_path = folder / file_name
        
        # Đọc nội dung file để tính MD5
        file_content = file.read()
        md5_checksum = hashlib.md5(file_content).hexdigest()
        
        # Lưu file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Tạo FileInfo object
        file_info = FileInfo(
            name=file_name,
            content_type=file.content_type,
            size=len(file_content),
            md5_checksum=md5_checksum,
            path=str(file_path),
            url=f"{self.url_prefix}{file_name}"
        )
        
        return file_info
    
    def read(self, file_management: FileManagement):
        """
        Đọc file từ filesystem
        
        Args:
            file_management: FileManagement object chứa thông tin file
            
        Returns:
            bytes: Nội dung file
        """
        with open(file_management.path, 'rb') as f:
            data = f.read()
        return data

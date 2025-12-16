from flask import g
from repositories.file_management_repository import FileManagementRepository
from repositories.file_repository import FileRepository
from dto.responses import FileResponse, FileURLResponse, BatchUploadResponse, FileData
from models.models import FileManagement
from exceptions.exceptions import AppException, ErrorCode


class FileService:
    """
    Service layer cho file management
    Xử lý business logic cho upload, download, và batch upload
    """
    
    def __init__(self, file_management_repository: FileManagementRepository,
                 file_repository: FileRepository):
        self.file_management_repository = file_management_repository
        self.file_repository = file_repository
    
    def upload(self, file):
        """
        Upload single file
        
        Args:
            file: FileStorage object từ Flask request
            
        Returns:
            FileResponse object
        """
        # Lưu file vào filesystem và lấy FileInfo
        file_info = self.file_repository.save(file)
        
        # Tạo FileManagement entity từ FileInfo
        file_management = FileManagement(
            id=file_info.name,  # Sử dụng tên file làm id
            user_id=g.user_id,  # Lấy user_id từ JWT token (được set trong decorator)
            md5checksum=file_info.md5_checksum,
            content_type=file_info.content_type,
            size=file_info.size,
            path=file_info.path
        )
        
        # Lưu metadata vào database
        self.file_management_repository.save(file_management)
        
        # Trả về response
        return FileResponse(
            original_file_name=file.filename,
            url=file_info.url
        )
    
    def download(self, file_name):
        """
        Download file
        
        Args:
            file_name: Tên file cần download
            
        Returns:
            FileData object chứa content_type và file content
        """
        # Tìm file metadata trong database
        file_management = self.file_management_repository.find_by_id(file_name)
        
        if file_management is None:
            raise AppException(ErrorCode.FILE_NOT_EXISTED)
        
        # Đọc file content từ filesystem
        resource = self.file_repository.read(file_management)
        
        return FileData(
            content_type=file_management.content_type,
            resource=resource
        )
    
    def batch_upload(self, files):
        """
        Upload multiple files
        
        Args:
            files: List của FileStorage objects
            
        Returns:
            BatchUploadResponse object
        """
        uploads = []
        user_id = g.user_id  # Lấy user_id từ JWT token
        
        for file in files:
            # Lưu file vào filesystem
            file_info = self.file_repository.save(file)
            
            # Tạo FileManagement entity
            file_management = FileManagement(
                id=file_info.name,
                user_id=user_id,
                md5checksum=file_info.md5_checksum,
                content_type=file_info.content_type,
                size=file_info.size,
                path=file_info.path
            )
            
            # Lưu metadata vào database
            self.file_management_repository.save(file_management)
            
            # Thêm vào list response
            uploads.append(FileURLResponse(url=file_info.url))
        
        return BatchUploadResponse(uploads=uploads)

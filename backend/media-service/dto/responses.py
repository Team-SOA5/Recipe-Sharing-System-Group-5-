from dataclasses import dataclass
from typing import List, Any, Optional


@dataclass
class ApiResponse:
    """
    Generic API response wrapper
    """
    code: int = 0
    message: str = "success!"
    data: Optional[Any] = None
    
    def to_dict(self):
        result = {
            'code': self.code,
            'message': self.message
        }
        if self.data is not None:
            result['data'] = self.data
        return result


@dataclass
class FileResponse:
    """
    Response cho single file upload
    """
    original_file_name: str
    url: str
    
    def to_dict(self):
        return {
            'originalFileName': self.original_file_name,
            'url': self.url
        }


@dataclass
class FileURLResponse:
    """
    Response chứa URL của file
    """
    url: str
    
    def to_dict(self):
        return {
            'url': self.url
        }


@dataclass
class BatchUploadResponse:
    """
    Response cho batch upload
    """
    uploads: List[FileURLResponse]
    
    def to_dict(self):
        return {
            'uploads': [upload.to_dict() for upload in self.uploads]
        }


@dataclass
class FileData:
    """
    Data class cho file download
    """
    content_type: str
    resource: bytes

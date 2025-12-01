from extensions import mongo
from bson import ObjectId
from datetime import datetime


class FileManagement:
    """
    Entity class for file management - 
    Lưu trữ thông tin file trong MongoDB collection 'file-management'
    """
    collection_name = 'file-management'
    
    def __init__(self, id=None, user_id=None, md5checksum=None, 
                 content_type=None, size=None, path=None):
        self._id = id  # MongoDB document id
        self.user_id = user_id
        self.md5checksum = md5checksum
        self.content_type = content_type
        self.size = size
        self.path = path
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'md5checksum': self.md5checksum,
            'content_type': self.content_type,
            'size': self.size,
            'path': self.path
        }
    
    @staticmethod
    def from_dict(data):
        """Tạo object từ dictionary"""
        if data is None:
            return None
        return FileManagement(
            id=str(data.get('_id')),
            user_id=data.get('user_id'),
            md5checksum=data.get('md5checksum'),
            content_type=data.get('content_type'),
            size=data.get('size'),
            path=data.get('path')
        )

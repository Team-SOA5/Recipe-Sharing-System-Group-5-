from extensions import mongo
from models.models import FileManagement
from bson import ObjectId


class FileManagementRepository:
    """
    Repository cho FileManagement - tương ứng với FileManagementRepository trong Java
    Xử lý các thao tác database với MongoDB collection 'file-management'
    """
    
    def __init__(self):
        # Collection chỉ được truy cập sau khi Flask app đã init Mongo
        self.collection_name = 'file-management'

    def _get_collection(self):
        db = mongo.db
        if db is None:
            raise RuntimeError('MongoDB connection chưa được khởi tạo')
        return db[self.collection_name]
    
    def save(self, file_management: FileManagement):
        """
        Lưu FileManagement vào database
        """
        data = file_management.to_dict()
        # Sử dụng _id từ file_management nếu có, nếu không MongoDB sẽ tự generate
        if data['_id']:
            data['_id'] = data['_id']
        else:
            data.pop('_id', None)
        
        result = self._get_collection().insert_one(data)
        file_management._id = str(result.inserted_id)
        return file_management
    
    def find_by_id(self, file_id: str):
        """
        Tìm FileManagement theo ID
        Returns: FileManagement object hoặc None nếu không tìm thấy
        """
        data = self._get_collection().find_one({'_id': file_id})
        return FileManagement.from_dict(data)
    
    def delete_by_id(self, file_id: str):
        """
        Xóa FileManagement theo ID
        """
        result = self._get_collection().delete_one({'_id': file_id})
        return result.deleted_count > 0
    
    def find_all(self):
        """
        Lấy tất cả FileManagement
        """
        data_list = self._get_collection().find()
        return [FileManagement.from_dict(data) for data in data_list]

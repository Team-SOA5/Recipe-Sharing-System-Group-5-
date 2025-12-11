from pymongo import MongoClient
from config import app_config

class MongoDB:
    def __init__(self):
        # Kết nối MongoDB bằng driver pymongo thuần
        # Lấy URI từ biến môi trường hoặc file config
        self.client = MongoClient(app_config.mongo_uri)
        
        # Tự động chọn database từ URI
        self.db = self.client.get_database()

# Khởi tạo instance
mongo = MongoDB()
from extensions import mongo
import datetime

class FileManagementRepository:
    def __init__(self):
        # Sử dụng mongo.db (từ extensions.py)
        self.collection = mongo.db['file-management']

    def save(self, file_data):
        file_data['created_at'] = datetime.datetime.utcnow()
        self.collection.insert_one(file_data)
        return file_data

    def find_by_filename(self, filename):
        return self.collection.find_one({"fileName": filename})
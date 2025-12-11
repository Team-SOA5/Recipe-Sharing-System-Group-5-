from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import datetime

class MedicalRecordModel:
    def __init__(self):
        # Lấy URI từ .env của bạn (đã có user/pass)
        mongo_uri = os.getenv('MONGO_URI')
        self.client = MongoClient(mongo_uri)
        
        # Tên DB lấy từ URI hoặc default
        db_name = mongo_uri.split('/')[-1].split('?')[0] or 'cookpad_health_db'
        self.db = self.client.get_database(db_name)
        self.collection = self.db.medical_records

    def _serialize(self, record):
        if not record:
            return None
        record['id'] = str(record['_id'])
        del record['_id']
        return record

    def create(self, data):
        data['uploadedAt'] = datetime.datetime.utcnow().isoformat()
        data['processedAt'] = None
        data['status'] = 'pending'
        data['errorMessage'] = None
        data['extractedText'] = ""
        data['extractedData'] = {}
        data['aiRecommendations'] = []
        
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def find_all(self, user_id, page=1, limit=10, status=None):
        query = {'userId': user_id}
        if status:
            query['status'] = status
        
        skip = (page - 1) * limit
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("uploadedAt", -1)
        total_docs = self.collection.count_documents(query)
        
        records = [self._serialize(doc) for doc in cursor]
        
        # Optimize list view
        for r in records:
            r.pop('extractedText', None)
            r.pop('extractedData', None)
            
        return records, total_docs

    def find_by_id(self, record_id, user_id):
        try:
            oid = ObjectId(record_id)
        except:
            return None
        return self._serialize(self.collection.find_one({'_id': oid, 'userId': user_id}))

    def update_status_and_data(self, record_id, status, extracted_text=None, extracted_data=None, error_msg=None):
        update_fields = {
            'status': status,
            'processedAt': datetime.datetime.utcnow().isoformat() if status == 'processed' else None
        }
        if extracted_text:
            update_fields['extractedText'] = extracted_text
        if extracted_data:
            update_fields['extractedData'] = extracted_data
        if error_msg:
            update_fields['errorMessage'] = error_msg

        self.collection.update_one({'_id': ObjectId(record_id)}, {'$set': update_fields})

    def delete(self, record_id, user_id):
        try:
            oid = ObjectId(record_id)
        except:
            return False
        result = self.collection.delete_one({'_id': oid, 'userId': user_id})
        return result.deleted_count > 0
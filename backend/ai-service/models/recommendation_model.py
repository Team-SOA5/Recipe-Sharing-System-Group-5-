from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import datetime

class RecommendationModel:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_URI'))
        self.db = self.client.get_database()
        self.collection = self.db.recommendations

    def _serialize(self, doc):
        if not doc: return None
        doc['id'] = str(doc['_id'])
        del doc['_id']
        return doc

    def create(self, data):
        data['createdAt'] = datetime.datetime.utcnow().isoformat()
        # Đảm bảo feedback mặc định là None hoặc rỗng khi mới tạo
        if 'feedback' not in data:
            data['feedback'] = None
            
        res = self.collection.insert_one(data)
        return str(res.inserted_id)

    def find_all(self, user_id, page=1, limit=10, record_id=None):
        query = {'userId': user_id}
        if record_id:
            query['medicalRecordId'] = record_id
            
        skip = (page - 1) * limit
        
        # Sort theo mới nhất trước (-1)
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("createdAt", -1)
        total = self.collection.count_documents(query)
        
        return [self._serialize(doc) for doc in cursor], total

    def find_by_id(self, rec_id, user_id):
        try:
            return self._serialize(self.collection.find_one({'_id': ObjectId(rec_id), 'userId': user_id}))
        except:
            return None

    def add_feedback(self, rec_id, user_id, feedback_data):
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(rec_id), 'userId': user_id},
                {'$set': {'feedback': feedback_data}}
            )
            return result.modified_count > 0
        except:
            return False

    def delete(self, rec_id, user_id):
        try:
            res = self.collection.delete_one({'_id': ObjectId(rec_id), 'userId': user_id})
            return res.deleted_count > 0
        except:
            return False
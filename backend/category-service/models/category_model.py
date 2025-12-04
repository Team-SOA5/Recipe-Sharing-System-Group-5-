import mongoengine as db
from datetime import datetime

class Category(db.Document):
    # id: string -> mongoengine tự tạo _id là ObjectId, ta sẽ convert sang string khi trả về
    name = db.StringField(required=True, unique=True)
    description = db.StringField()
    icon = db.StringField() # URL icon
    recipesCount = db.IntField(default=0) # Số lượng công thức thuộc danh mục này
    
    createdAt = db.DateTimeField(default=datetime.utcnow) # Đổi tên biến cho khớp schema openapi
    updatedAt = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'categories',
        'ordering': ['name']
    }

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "recipesCount": self.recipesCount,
            "createdAt": self.createdAt.isoformat()
        }
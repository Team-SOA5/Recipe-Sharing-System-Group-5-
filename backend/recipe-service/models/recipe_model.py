import mongoengine as db
from datetime import datetime

class Ingredient(db.EmbeddedDocument):
    name = db.StringField(required=True)
    quantity = db.StringField(required=True)

class Step(db.EmbeddedDocument):
    order = db.IntField(required=True)
    content = db.StringField(required=True)
    image = db.StringField()

class Recipe(db.Document):
    title = db.StringField(required=True)
    description = db.StringField()
    thumbnail = db.StringField()
    
    ingredients = db.ListField(db.EmbeddedDocumentField(Ingredient))
    steps = db.ListField(db.EmbeddedDocumentField(Step))
    
    difficulty = db.StringField(choices=('Easy', 'Medium', 'Hard'), default='Medium')
    time_minutes = db.IntField()
    serving = db.IntField()
    
    author_id = db.StringField(required=True) # User ID từ token
    category_id = db.StringField()
    tags = db.ListField(db.StringField())
    
    # Calo (Optional - User nhập)
    calories = db.FloatField(default=0.0)
    
    # Thống kê
    views = db.IntField(default=0)
    average_rating = db.FloatField(default=0.0)
    
    created_at = db.DateTimeField(default=datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'recipes',
        'ordering': ['-created_at']
    }

    def to_json_summary(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "thumbnail": self.thumbnail,
            "author_id": self.author_id,
            "total_time": self.time_minutes,
            "difficulty": self.difficulty,
            "average_rating": self.average_rating,
            "views": self.views,
            "created_at": self.created_at.isoformat()
        }

    def to_json_detail(self):
        data = self.to_json_summary()
        data.update({
            "description": self.description,
            "ingredients": [{"name": i.name, "quantity": i.quantity} for i in self.ingredients],
            "steps": [{"order": s.order, "content": s.content, "image": s.image} for s in self.steps],
            "serving": self.serving,
            "category_id": self.category_id,
            "tags": self.tags,
            "calories": self.calories,
            "updated_at": self.updated_at.isoformat()
        })
        return data
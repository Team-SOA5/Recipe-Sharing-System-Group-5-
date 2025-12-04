import mongoengine as db
from datetime import datetime

# --- Sub-documents ---

class Ingredient(db.EmbeddedDocument):
    name = db.StringField(required=True)
    amount = db.StringField(required=True) # Đổi quantity -> amount cho khớp openapi
    note = db.StringField()

class Instruction(db.EmbeddedDocument): # Đổi Step -> Instruction
    step = db.IntField(required=True)   # Đổi order -> step
    description = db.StringField(required=True) # Đổi content -> description
    image = db.StringField()
    duration = db.IntField() # Thời gian của bước này (phút)

class NutritionInfo(db.EmbeddedDocument):
    calories = db.IntField(default=0)
    protein = db.FloatField(default=0.0)
    carbs = db.FloatField(default=0.0)
    fat = db.FloatField(default=0.0)
    fiber = db.FloatField(default=0.0)

# --- Main Document ---

class Recipe(db.Document):
    # Thông tin cơ bản
    title = db.StringField(required=True)
    description = db.StringField()
    thumbnail = db.StringField()
    
    # Chi tiết
    ingredients = db.ListField(db.EmbeddedDocumentField(Ingredient))
    instructions = db.ListField(db.EmbeddedDocumentField(Instruction))
    images = db.ListField(db.StringField()) # Danh sách ảnh thêm
    tips = db.ListField(db.StringField())   # Mẹo nấu ăn
    
    # Phân loại & Chỉ số
    author_id = db.StringField(required=True)
    category_id = db.StringField()
    difficulty = db.StringField(choices=('easy', 'medium', 'hard'), default='medium')
    
    cookingTime = db.IntField() # Đổi time_minutes -> cookingTime
    servings = db.IntField()
    
    tags = db.ListField(db.StringField())
    nutritionInfo = db.EmbeddedDocumentField(NutritionInfo, default=NutritionInfo)
    
    # Thống kê & Tương tác
    averageRating = db.FloatField(default=0.0)
    ratingsCount = db.IntField(default=0)
    viewsCount = db.IntField(default=0)     # Đổi views -> viewsCount
    favoritesCount = db.IntField(default=0)
    commentsCount = db.IntField(default=0)
    
    # Timestamps
    createdAt = db.DateTimeField(default=datetime.utcnow)
    updatedAt = db.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'recipes',
        'ordering': ['-createdAt']
    }

    # Helper chuyển đổi JSON (Khớp schema Recipe trong OpenAPI)
    def to_json_summary(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "author": {"id": self.author_id}, # Frontend sẽ fetch chi tiết User sau
            "category": {"id": self.category_id}, # Frontend fetch Category sau
            "difficulty": self.difficulty,
            "cookingTime": self.cookingTime,
            "servings": self.servings,
            "averageRating": self.averageRating,
            "ratingsCount": self.ratingsCount,
            "viewsCount": self.viewsCount,
            "favoritesCount": self.favoritesCount,
            "commentsCount": self.commentsCount,
            "tags": self.tags,
            "createdAt": self.createdAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
            "isFavorited": False # Logic check favorite sẽ làm sau hoặc ở service khác
        }

    # Helper chuyển đổi JSON Chi tiết (Khớp schema RecipeDetail)
    def to_json_detail(self):
        data = self.to_json_summary()
        data.update({
            "ingredients": [
                {"name": i.name, "amount": i.amount, "note": i.note} 
                for i in self.ingredients
            ],
            "instructions": [
                {"step": s.step, "description": s.description, "image": s.image, "duration": s.duration} 
                for s in self.instructions
            ],
            "images": self.images,
            "nutritionInfo": {
                "calories": self.nutritionInfo.calories,
                "protein": self.nutritionInfo.protein,
                "carbs": self.nutritionInfo.carbs,
                "fat": self.nutritionInfo.fat,
                "fiber": self.nutritionInfo.fiber
            },
            "tips": self.tips
        })
        return data
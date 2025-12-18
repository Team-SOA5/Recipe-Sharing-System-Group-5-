from datetime import datetime
from bson import ObjectId
from typing import Optional


class Tag:
    """
    Tag model representing a tag entity in MongoDB
    Equivalent to Tag.java entity
    """
    
    def __init__(
        self,
        name: str,
        created_at: Optional[datetime] = None,
        recipes_count: int = 0,
        _id: Optional[ObjectId] = None
    ):
        self.id = _id
        self.name = name
        self.created_at = created_at or datetime.utcnow()
        self.recipes_count = recipes_count
    
    def to_dict(self):
        """Convert Tag object to dictionary for MongoDB"""
        doc = {
            'name': self.name,
            'createdAt': self.created_at,
            'recipesCount': self.recipes_count
        }
        if self.id:
            doc['_id'] = self.id
        return doc
    
    @staticmethod
    def from_dict(doc: dict) -> 'Tag':
        """Create Tag object from MongoDB document"""
        if not doc:
            return None
        return Tag(
            _id=doc.get('_id'),
            name=doc.get('name'),
            created_at=doc.get('createdAt'),
            recipes_count=doc.get('recipesCount', 0)
        )
    
    def __repr__(self):
        return f"Tag(id={self.id}, name={self.name}, recipes_count={self.recipes_count})"

from typing import List, Optional
from bson import ObjectId
from extensions import mongo
from models.models import Tag
import re


class TagRepository:
    """
    Tag repository for database operations
    Equivalent to TagRepository.java interface
    """
    
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        """Lazy initialization of MongoDB collection"""
        if self._collection is None:
            self._collection = mongo.db.tag
        return self._collection
    
    def save(self, tag: Tag) -> Tag:
        """
        Save or update a tag
        Equivalent to MongoRepository.save()
        """
        tag_doc = tag.to_dict()
        
        if tag.id:
            # Update existing tag
            self.collection.update_one(
                {'_id': tag.id},
                {'$set': tag_doc}
            )
        else:
            # Insert new tag
            result = self.collection.insert_one(tag_doc)
            tag.id = result.inserted_id
        
        return tag
    
    def find_by_name(self, name: str) -> Optional[Tag]:
        """
        Find tag by name
        Equivalent to TagRepository.findByName()
        """
        doc = self.collection.find_one({'name': name})
        return Tag.from_dict(doc) if doc else None
    
    def find_all_by_name_like(self, keyword: str, skip: int = 0, limit: int = 20, sort_field: str = 'createdAt', sort_order: int = -1) -> List[Tag]:
        """
        Find all tags by name matching keyword with pagination and sorting
        Equivalent to TagRepository.findAllByNameLike() with Pageable
        
        Args:
            keyword: Search keyword for name
            skip: Number of documents to skip (for pagination)
            limit: Maximum number of documents to return
            sort_field: Field to sort by
            sort_order: Sort order (1 for ascending, -1 for descending)
        """
        # Create regex pattern for case-insensitive partial match
        pattern = re.compile(keyword, re.IGNORECASE)
        
        cursor = self.collection.find(
            {'name': {'$regex': pattern}}
        ).sort(sort_field, sort_order).skip(skip).limit(limit)
        
        return [Tag.from_dict(doc) for doc in cursor]
    
    def find_all(self, skip: int = 0, limit: int = 20, sort_field: str = 'recipesCount', sort_order: int = -1) -> List[Tag]:
        """
        Find all tags with pagination and sorting
        Equivalent to MongoRepository.findAll(Pageable)
        
        Args:
            skip: Number of documents to skip (for pagination)
            limit: Maximum number of documents to return
            sort_field: Field to sort by
            sort_order: Sort order (1 for ascending, -1 for descending)
        """
        cursor = self.collection.find().sort(sort_field, sort_order).skip(skip).limit(limit)
        
        return [Tag.from_dict(doc) for doc in cursor]
    
    def find_by_id(self, tag_id: str) -> Optional[Tag]:
        """
        Find tag by ID
        Equivalent to MongoRepository.findById()
        """
        try:
            doc = self.collection.find_one({'_id': ObjectId(tag_id)})
            return Tag.from_dict(doc) if doc else None
        except Exception:
            return None
    
    def delete_by_id(self, tag_id: str) -> bool:
        """
        Delete tag by ID
        Equivalent to MongoRepository.deleteById()
        """
        try:
            result = self.collection.delete_one({'_id': ObjectId(tag_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    def count(self) -> int:
        """
        Count total number of tags
        Equivalent to MongoRepository.count()
        """
        return self.collection.count_documents({})

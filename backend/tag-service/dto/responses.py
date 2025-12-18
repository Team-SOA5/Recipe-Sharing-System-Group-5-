from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class TagResponse:
    """
    Tag response DTO
    Equivalent to TagResponse.java
    """
    id: str
    name: str
    created_at: str
    recipes_count: int
    
    def __init__(self, id: str, name: str, created_at: datetime, recipes_count: int):
        self.id = id
        self.name = name
        # Convert datetime to ISO format string
        if isinstance(created_at, datetime):
            self.created_at = created_at.isoformat()
        else:
            self.created_at = created_at
        self.recipes_count = recipes_count
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'createdAt': self.created_at,
            'recipesCount': self.recipes_count
        }
    
    @staticmethod
    def from_tag(tag) -> 'TagResponse':
        """Create TagResponse from Tag model"""
        return TagResponse(
            id=str(tag.id),
            name=tag.name,
            created_at=tag.created_at,
            recipes_count=tag.recipes_count
        )


@dataclass
class TagList:
    """
    Tag list response DTO
    Equivalent to TagList.java
    """
    tag_response_list: List[TagResponse]
    
    def __init__(self, tag_response_list: List[TagResponse]):
        self.tag_response_list = tag_response_list
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'tagResponseList': [tag.to_dict() for tag in self.tag_response_list]
        }


@dataclass
class ApiResponse:
    """
    Generic API response wrapper
    Equivalent to ApiResponse.java
    """
    code: int = 0
    message: str = "success!"
    data: Optional[any] = None
    
    def to_dict(self):
        """Convert to dictionary"""
        result = {
            'code': self.code,
            'message': self.message
        }
        if self.data is not None:
            if hasattr(self.data, 'to_dict'):
                result['data'] = self.data.to_dict()
            else:
                result['data'] = self.data
        return result

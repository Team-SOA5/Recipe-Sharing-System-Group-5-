from typing import List
from datetime import datetime
from models.models import Tag
from repositories.tag_repository import TagRepository
from dto.requests import TagRequest
from dto.responses import TagResponse, TagList


class TagService:
    """
    Tag service containing business logic
    Equivalent to TagService.java
    """
    
    def __init__(self):
        self.tag_repository = TagRepository()
    
    def create(self, request: TagRequest) -> TagResponse:
        """
        Create or update a tag
        If tag exists, increment recipes_count
        If tag doesn't exist, create new tag with recipes_count = 1
        
        Equivalent to TagService.create()
        """
        # Find existing tag by name
        tag = self.tag_repository.find_by_name(request.name)
        
        if tag is None:
            # Create new tag
            tag = Tag(
                name=request.name,
                created_at=datetime.utcnow(),
                recipes_count=1
            )
        else:
            # Update existing tag
            tag.recipes_count += 1
        
        # Save tag to database
        saved_tag = self.tag_repository.save(tag)
        
        # Convert to response DTO
        return TagResponse.from_tag(saved_tag)
    
    def find_by_key(self, keyword: str, size: int) -> TagList:
        """
        Find tags by keyword with pagination
        Sort by createdAt descending
        
        Equivalent to TagService.findByKey()
        """
        # Find tags matching keyword, sorted by createdAt descending
        tags = self.tag_repository.find_all_by_name_like(
            keyword=keyword,
            skip=0,
            limit=size,
            sort_field='createdAt',
            sort_order=-1  # -1 for descending
        )
        
        # Convert to response DTOs
        tag_responses = [TagResponse.from_tag(tag) for tag in tags]
        
        return TagList(tag_response_list=tag_responses)
    
    def find_by_popular(self, size: int) -> TagList:
        """
        Find most popular tags (by recipes count)
        Sort by recipesCount descending
        
        Equivalent to TagService.findByPopular()
        """
        # Find all tags, sorted by recipesCount descending
        tags = self.tag_repository.find_all(
            skip=0,
            limit=size,
            sort_field='recipesCount',
            sort_order=-1  # -1 for descending
        )
        
        # Convert to response DTOs
        tag_responses = [TagResponse.from_tag(tag) for tag in tags]
        
        return TagList(tag_response_list=tag_responses)

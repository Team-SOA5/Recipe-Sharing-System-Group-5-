from dataclasses import dataclass
from typing import Optional


@dataclass
class TagRequest:
    """
    Tag request DTO
    Equivalent to TagRequest.java
    """
    name: str
    
    def __init__(self, name: str):
        self.name = name
    
    @staticmethod
    def from_dict(data: dict) -> 'TagRequest':
        """Create TagRequest from dictionary"""
        return TagRequest(name=data.get('name', ''))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'name': self.name
        }

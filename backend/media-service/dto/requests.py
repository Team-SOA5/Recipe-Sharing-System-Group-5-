from dataclasses import dataclass
from typing import Optional


@dataclass
class FileInfo:
    """
    DTO cho thông tin file
    Được sử dụng để truyền thông tin file giữa các layer
    """
    name: str
    content_type: str
    size: int
    md5_checksum: str
    path: str
    url: str
    
    def __init__(self, name=None, content_type=None, size=None, 
                 md5_checksum=None, path=None, url=None):
        self.name = name
        self.content_type = content_type
        self.size = size
        self.md5_checksum = md5_checksum
        self.path = path
        self.url = url

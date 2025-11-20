import requests
from flask import request
from config import Config
from dto.responses import FileResponse
import logging

logger = logging.getLogger(__name__)


class MediaClient:
    """HTTP Client for communicating with Media Service (Feign equivalent)"""
    
    def __init__(self):
        self.base_url = Config.MEDIA_SERVICE_URL
    
    def upload_media(self, file) -> FileResponse:
        """
        Upload media file to media service
        Equivalent to FileClient.uploadMedia in Java
        """
        try:
            # Get authorization header from current request
            auth_header = request.headers.get('Authorization', '')
            
            headers = {}
            if auth_header:
                headers['Authorization'] = auth_header
                logger.info(f"Header: {auth_header}")
            
            # Prepare file for upload
            files = {
                'file': (file.filename, file.stream, file.content_type)
            }
            
            # Make POST request to media service
            url = f"{self.base_url}/upload"
            logger.info(f"Uploading file to: {url}")
            
            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            return FileResponse.from_dict(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error uploading file to media service: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")

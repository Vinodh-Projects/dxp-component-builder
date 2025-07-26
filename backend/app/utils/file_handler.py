import os
import uuid
import base64
import logging
from typing import Optional
from fastapi import UploadFile
import aiofiles
import hashlib

logger = logging.getLogger(__name__)

class FileHandler:
    """Handle file uploads and storage"""
    
    def __init__(self, upload_dir: str = "/tmp/aem_uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    async def upload_image(self, file: UploadFile) -> str:
        """Upload image and return base64 encoded data URL for OpenAI Vision API"""
        
        logger.info(f"Processing image upload: {file.filename}, content_type: {file.content_type}, size: {file.size}")
        
        # Validate file
        await self._validate_image_file(file)
        
        # Read file content
        content = await file.read()
        actual_size = len(content)
        
        logger.info(f"Image content read successfully: {actual_size} bytes")
        
        # Get file extension and determine MIME type
        filename = file.filename or "image.png"
        file_extension = filename.split('.')[-1].lower()
        mime_type_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        
        mime_type = mime_type_map.get(file_extension, 'image/png')
        logger.info(f"Detected MIME type: {mime_type} for extension: {file_extension}")
        
        # Convert to base64
        base64_content = base64.b64encode(content).decode('utf-8')
        
        # Return data URL format expected by OpenAI Vision API
        data_url = f"data:{mime_type};base64,{base64_content}"
        
        # Log data URL length (for debugging, don't log the actual content)
        logger.info(f"Generated data URL with {len(base64_content)} base64 characters")
        
        # Optionally, also save the file locally for backup/debugging
        file_id = str(uuid.uuid4())
        backup_filename = f"{file_id}.{file_extension}"
        filepath = os.path.join(self.upload_dir, backup_filename)
        
        try:
            async with aiofiles.open(filepath, 'wb') as f:
                await f.write(content)
            logger.info(f"Image saved locally: {filepath}")
        except Exception as e:
            logger.warning(f"Could not save file locally: {e}")
        
        return data_url
    
    async def _validate_image_file(self, file: UploadFile):
        """Validate uploaded image file"""
        logger.info(f"Validating image file: {file.filename}")
        
        # Check file size (max 20MB for OpenAI Vision API)
        max_size = 20 * 1024 * 1024  # 20MB
        if file.size and file.size > max_size:
            logger.error(f"Image file too large: {file.size} bytes")
            raise ValueError(f"Image file too large: {file.size} bytes. Maximum allowed: {max_size} bytes")
        
        # Check file extension
        filename = file.filename or ""
        valid_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
        
        if file_extension not in valid_extensions:
            logger.error(f"Invalid image format: {file_extension}")
            raise ValueError(f"Invalid image format: {file_extension}. Supported formats: {', '.join(valid_extensions)}")
        
        # Check content type
        content_type = file.content_type or ""
        valid_content_types = {'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'}
        
        if content_type not in valid_content_types:
            logger.warning(f"Unexpected content type: {content_type}. Proceeding with extension-based detection.")
        
        logger.info(f"Image validation passed: {file_extension} format, {file.size} bytes")
    
    async def delete_file(self, filepath: str):
        """Delete uploaded file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Error deleting file: {e}")
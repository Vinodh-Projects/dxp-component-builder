import os
import uuid
from typing import Optional
from fastapi import UploadFile
import aiofiles
import hashlib

class FileHandler:
    """Handle file uploads and storage"""
    
    def __init__(self, upload_dir: str = "/tmp/aem_uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    async def upload_image(self, file: UploadFile) -> str:
        """Upload image and return URL/path"""
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.{file_extension}"
        filepath = os.path.join(self.upload_dir, filename)
        
        # Save file
        async with aiofiles.open(filepath, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # In production, upload to S3/CDN and return public URL
        # For now, return local path
        return f"file://{filepath}"
    
    async def delete_file(self, filepath: str):
        """Delete uploaded file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Error deleting file: {e}")
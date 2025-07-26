#!/usr/bin/env python3
"""
Test script to verify the image upload fix for OpenAI Vision API
"""

import asyncio
import base64
import io
from PIL import Image
from backend.app.utils.file_handler import FileHandler
from fastapi import UploadFile

async def test_image_conversion():
    """Test that images are properly converted to base64 data URLs"""
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Create a mock UploadFile
    class MockUploadFile:
        def __init__(self, content: bytes, filename: str, content_type: str):
            self.content = content
            self.filename = filename
            self.content_type = content_type
            self.size = len(content)
        
        async def read(self):
            return self.content
    
    # Test the file handler
    file_handler = FileHandler()
    mock_file = MockUploadFile(
        content=img_bytes.getvalue(),
        filename="test_image.png",
        content_type="image/png"
    )
    
    try:
        # This should return a data URL now instead of file:// URL
        result = await file_handler.upload_image(mock_file)
        
        print(f"✅ Upload successful!")
        print(f"Result type: {type(result)}")
        print(f"Result starts with: {result[:50]}...")
        print(f"Is data URL: {result.startswith('data:image/')}")
        print(f"Contains base64: {'base64' in result}")
        
        # Verify it's a proper data URL
        if result.startswith('data:image/png;base64,'):
            print("✅ Proper data URL format")
            
            # Try to decode the base64 part
            base64_part = result.split(',')[1]
            decoded = base64.b64decode(base64_part)
            print(f"✅ Base64 decoding successful, {len(decoded)} bytes")
        else:
            print("❌ Not a proper data URL format")
            
    except Exception as e:
        print(f"❌ Error during upload: {e}")

if __name__ == "__main__":
    print("Testing image upload fix...")
    asyncio.run(test_image_conversion())

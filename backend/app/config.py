from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Service Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    WORKERS: int = 4
    
    # Model Configuration
    GPT4_MODEL: str = "gpt-4o"  # Updated to current model
    GPT4_VISION_MODEL: str = "gpt-4o"  # Updated to current model
    CLAUDE_MODEL: str = "claude-3-opus-20240229"
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 300  # 5 minutes
    CACHE_TTL: int = 3600  # 1 hour
    
    # Redis Configuration (for caching and queue)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Component Generation Settings
    MAX_RETRIES: int = 3
    ENABLE_VALIDATION: bool = True
    ENABLE_CACHING: bool = True
    
    # Default AEM Project Configuration
    DEFAULT_APP_ID: str = "myapp"
    DEFAULT_PACKAGE_NAME: str = "com.mycompany.myapp"
    
    class Config:
        env_file = ".env"

settings = Settings()

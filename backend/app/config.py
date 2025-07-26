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
    GPT4_VISION_MODEL: str = "o4-mini"  # Updated to current model
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
    DEFAULT_APP_ID: str = "wknd"
    DEFAULT_PACKAGE_NAME: str = "com.adobe.aem.guides.wknd"
    AI_COMPONENTS_SUBFOLDER: str = "wkndai"
    
    # Project Organization Settings
    PROJECT_CODE_PATH: str = "/app/project_code"
    AUTO_ORGANIZE_COMPONENTS: bool = True
    BACKUP_EXISTING_COMPONENTS: bool = True
    
    # AEM Deployment Settings
    AEM_AUTHOR_URL: str = "http://host.docker.internal:4502"
    AEM_USERNAME: str = "admin"
    AEM_PASSWORD: str = "admin"
    MAVEN_PROFILES: str = "adobe-public,autoInstallPackage"
    SKIP_TESTS: bool = True
    AEM_MOCK_MODE: bool = False  # Disable mock mode to use real AEM server
    
    class Config:
        env_file = ".env"

settings = Settings()

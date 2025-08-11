from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os


"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import Field
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Nhan88ng API"
    VERSION: str = "1.0.0"
    
    # Shop Configuration
    SHOPS_CONFIG_FILE: str = "shops.json"
    
    # CORS Settings - Read from .env
    CORS_ORIGINS_STR: str = Field(alias="CORS_ORIGINS")
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Convert CORS origins string to list"""
        if hasattr(self, '_cors_origins_list'):
            return self._cors_origins_list
        
        origins = self.CORS_ORIGINS_STR
        if isinstance(origins, str):
            self._cors_origins_list = [origin.strip() for origin in origins.split(',') if origin.strip()]
        else:
            self._cors_origins_list = origins
        return self._cors_origins_list
    
    # MongoDB Atlas Configuration - Read from .env file
    MONGODB_SHARED_URL: str
    
    # JWT Configuration - Read from .env file
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    
    # Email Configuration - Read from .env
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str
    FROM_NAME: str
    
    # Frontend URLs - Read from .env
    FRONTEND_URL: str
    
    # Security Settings
    PASSWORD_MIN_LENGTH: int = 8
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Server Configuration - Read from .env
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "info"
    
    # Test Credentials - ALL READ FROM .env FOR SECURITY
    TEST_USER_PASSWORD: str
    BASE_URL: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Don't validate assignment to avoid issues with property setters
        validate_assignment = False

settings = Settings()

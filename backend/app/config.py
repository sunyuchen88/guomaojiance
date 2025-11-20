from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables"""

    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:postgres123@localhost:5432/food_quality"

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 2

    # Client API Configuration
    API_BASE_URL: str = "https://test1.yunxianpei.com"
    CLIENT_APP_ID: str = "689_abc"
    CLIENT_SECRET: str = "67868790"

    # Server Configuration
    SERVER_DOMAIN: str = "http://localhost:8000"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost"

    # File Storage
    FILE_STORAGE_PATH: str = "/uploads/reports"
    MAX_FILE_SIZE_MB: int = 10

    # Sync Configuration
    SYNC_INTERVAL_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_origins_list(self) -> list:
        """Parse ALLOWED_ORIGINS string into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Create global settings instance
settings = Settings()

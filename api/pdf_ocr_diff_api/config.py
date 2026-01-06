"""Configuration settings for the PDF OCR Diff API."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    app_name: str = "PDF OCR Diff API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Configuration
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # File Upload Configuration
    max_file_size: int = 52428800  # 50MB in bytes
    allowed_file_types: List[str] = [".pdf"]
    
    # Logging Configuration
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_prefix="PDF_DIFF_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
settings = Settings()

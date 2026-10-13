from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Processor service configuration."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Environment
    ENV: str = "development"
    LOG_LEVEL: str = "info"
    PROCESSOR_PORT: int = 8000
    PROCESSOR_HOST: str = "0.0.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://dca_user:dca_secure_password@localhost:5432/dca_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Storage
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin123"
    S3_BUCKET_NAME: str = "dca-documents"
    S3_USE_SSL: bool = False
    
    # AI Engine
    AI_PROVIDER: str = "mock"  # "mock", "gemini", "openai"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    AI_MODEL_NAME: str = "gemini-1.5-pro"
    
    # Extraction & Validation thresholds
    CONFIDENCE_THRESHOLD: float = 0.75
    MAX_FILE_SIZE_MB: int = 50
    CHUNK_SIZE_TOKENS: int = 3000
    CHUNK_OVERLAP_TOKENS: int = 200


settings = Settings()

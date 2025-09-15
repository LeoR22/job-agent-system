from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str
    test_database_url: str
    
    # Redis
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str
    openai_org_id: Optional[str] = None
    
    # External APIs
    linkedin_api_key: Optional[str] = None
    indeed_api_key: Optional[str] = None
    glassdoor_api_key: Optional[str] = None
    
    # File Upload
    upload_dir: str = "uploads/"
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = ["pdf", "doc", "docx"]
    
    # MCP Configuration
    mcp_api_key: Optional[str] = None
    mcp_base_url: str = "https://api.mcp.example.com"
    
    # Application
    app_name: str = "Job Agent System"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_metrics: bool = True
    
    # Email
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
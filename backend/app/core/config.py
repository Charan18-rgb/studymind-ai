from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # AI Configuration
    gemini_api_key: str = ""
    demo_mode: bool = False
    debug: bool = True
    test_mode: bool = False
    auth_secret: str = "change-this-development-secret-before-deploying"
    session_hours: int = 24
    upload_max_bytes: int = 10 * 1024 * 1024
    upload_directory: str = "data/uploads"

    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./studymind.db"

    # Backend Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Frontend Configuration
    frontend_port: int = 5173

    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

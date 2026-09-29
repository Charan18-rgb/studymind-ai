from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # AI Configuration
    gemini_api_key: str = ""
    demo_mode: bool = False

    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./studymind.db"

    # Backend Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Frontend Configuration
    frontend_port: int = 5173

    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

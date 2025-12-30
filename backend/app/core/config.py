"""
Application Configuration
"""
import os
from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings and environment variables"""
    
    # Application
    PROJECT_NAME: str = "Vylos"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Database Settings
    POSTGRES_USER: str = "vylos"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "vylos_db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_HOST: str = "localhost"

    # Security Settings
    SECRET_KEY: str = "super-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # GitHub OAuth Settings
    GITHUB_CLIENT_ID: str = "your_github_client_id_here"
    GITHUB_CLIENT_SECRET: str = "your_github_client_secret_here"
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str = "your_google_client_id_here"
    GOOGLE_CLIENT_SECRET: str = "your_google_client_secret_here"

    # Deployment Settings
    HOST_PROJECTS_PATH: str = "D:/projects/vylos/projects"

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(current_file_dir, "..", "..", ".env")
        extra = "ignore"
        case_sensitive = True


settings = Settings()

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- Database Settings ---
    POSTGRES_USER: str = "vylos"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "vylos_db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_HOST: str = "localhost"

    # --- Security Settings ---
    SECRET_KEY: str = "super-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- GitHub OAuth Settings ---
    GITHUB_CLIENT_ID: str = "your_github_client_id_here"
    GITHUB_CLIENT_SECRET: str = "your_github_client_secret_here"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = "your_google_client_id_here"
    GOOGLE_CLIENT_SECRET: str = "your_google_client_secret_here"

    # --- Deployment Settings ---
    HOST_PROJECTS_PATH: str = "D:/projects/vylos/backend/projects"

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(current_file_dir, "..", ".env")
        extra = "ignore"

settings = Settings()
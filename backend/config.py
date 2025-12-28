import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    POSTGRES_HOST: str = "localhost"

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        # 1. Get the folder where THIS file (config.py) is located
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Go up one level (to vylos-docker root) and look for .env
        env_file = os.path.join(current_file_dir, "..", ".env")
        
        extra = "ignore"

settings = Settings()
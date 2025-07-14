from pydantic_settings import BaseSettings
from typing import List
import os
from fastapi.middleware.cors import CORSMiddleware


class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    
    # Database
    database_url: str = "sqlite:///./academy.db"
    
    # Redis (Celery 브로커)
    redis_url: str = "redis://localhost:6379"
    
    # JWT
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Firebase
    firebase_api_key: str = "AIzaSyAo9FU7YNkepYGy4zeqqj_CM_SBcdOYSn8"
    firebase_project_id: str = "academy-ai-assistant"
    
    # Gemini API
    gemini_api_key: str = "your-gemini-api-key"
    
    # Google Cloud Storage
    gcs_bucket_name: str = "academy-ai-assistant-files"
    gcs_credentials_path: str = "path/to/service-account-key.json"
    
    # CORS - 환경별 설정
    @property
    def allowed_origins(self) -> List[str]:
        if self.environment == "development":
            return [
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://localhost:3002",
                "http://localhost:3003",
                "http://121.165.240.250:3000",
                "http://121.165.240.250:3001",
                "http://121.165.240.250:3002",
                "http://121.165.240.250:3003",
            ]
        elif self.environment == "production":
            return [
                "https://your-domain.com",
                "https://www.your-domain.com",
            ]
        else:
            return []
    
    # Debug
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings() 
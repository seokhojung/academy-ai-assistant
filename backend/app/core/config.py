from pydantic_settings import BaseSettings
from typing import List
import os
from fastapi.middleware.cors import CORSMiddleware


class Settings(BaseSettings):
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./academy.db")
    
    # Redis (Celery 브로커)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Firebase
    firebase_api_key: str = os.getenv("FIREBASE_API_KEY", "AIzaSyAo9FU7YNkepYGy4zeqqj_CM_SBcdOYSn8")
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "academy-ai-assistant")
    
    # Gemini API
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
    
    # Google Cloud Storage
    gcs_bucket_name: str = os.getenv("GCS_BUCKET_NAME", "academy-ai-assistant-files")
    gcs_credentials_path: str = os.getenv("GCS_CREDENTIALS_PATH", "path/to/service-account-key.json")
    
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
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    class Config:
        env_file = ".env"

settings = Settings() 
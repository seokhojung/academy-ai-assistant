from typing import List
import os
from decouple import config
from fastapi.middleware.cors import CORSMiddleware


class Settings:
    # Environment
    environment: str = config("ENVIRONMENT", default="development")
    
    # Database
    database_url: str = config("DATABASE_URL", default="sqlite:///./academy.db")
    
    # Redis (Celery 브로커)
    redis_url: str = config("REDIS_URL", default="redis://localhost:6379")
    
    # JWT
    jwt_secret_key: str = config("JWT_SECRET_KEY", default="your-super-secret-jwt-key-change-in-production")
    jwt_algorithm: str = config("JWT_ALGORITHM", default="HS256")
    access_token_expire_minutes: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    # Firebase
    firebase_api_key: str = config("FIREBASE_API_KEY", default="AIzaSyAo9FU7YNkepYGy4zeqqj_CM_SBcdOYSn8")
    firebase_project_id: str = config("FIREBASE_PROJECT_ID", default="academy-ai-assistant")
    
    # Gemini API
    gemini_api_key: str = config("GEMINI_API_KEY", default="your-gemini-api-key")
    
    # Google Cloud Storage
    gcs_bucket_name: str = config("GCS_BUCKET_NAME", default="academy-ai-assistant-files")
    gcs_credentials_path: str = config("GCS_CREDENTIALS_PATH", default="path/to/service-account-key.json")
    
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
                "https://academy-ai-assistants.vercel.app",
                "https://academy-ai-assistant.vercel.app",
                "https://*.vercel.app",
                "https://your-domain.com",
                "https://www.your-domain.com",
            ]
        else:
            return []
    
    # Debug
    debug: bool = config("DEBUG", default=True, cast=bool)

settings = Settings() 
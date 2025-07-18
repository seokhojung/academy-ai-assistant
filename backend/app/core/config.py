from typing import List
import os
from decouple import config
from fastapi.middleware.cors import CORSMiddleware


class Settings:
    # Environment
    environment: str = str(config("ENVIRONMENT", default="development"))
    
    # Database
    database_url: str = str(config("DATABASE_URL", default="sqlite:///./academy.db"))
    
    # 로컬 개발 시 SQLite 사용
    @property
    def get_database_url(self) -> str:
        if self.environment == "development" and not os.getenv("DATABASE_URL"):
            return "sqlite:///./academy.db"
        return self.database_url
    
    # Redis (Celery 브로커)
    redis_url: str = str(config("REDIS_URL", default="redis://localhost:6379"))
    
    # JWT
    jwt_secret_key: str = str(config("JWT_SECRET_KEY", default="your-super-secret-jwt-key-change-in-production"))
    jwt_algorithm: str = str(config("JWT_ALGORITHM", default="HS256"))
    access_token_expire_minutes: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    # Firebase
    firebase_api_key: str = str(config("FIREBASE_API_KEY", default=""))
    firebase_project_id: str = str(config("FIREBASE_PROJECT_ID", default=""))
    
    # Gemini API
    gemini_api_key: str = str(config("GEMINI_API_KEY", default="your-gemini-api-key"))
    
    # Google Cloud Storage
    gcs_bucket_name: str = str(config("GCS_BUCKET_NAME", default="academy-ai-assistant-files"))
    gcs_credentials_path: str = str(config("GCS_CREDENTIALS_PATH", default="path/to/service-account-key.json"))
    
    # CORS - 환경별 설정
    @property
    def allowed_origins(self) -> List[str]:
        # 모든 환경에서 Vercel 도메인 허용
        origins = [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:3002",
            "http://localhost:3003",
            "http://121.165.240.250:3000",
            "http://121.165.240.250:3001",
            "http://121.165.240.250:3002",
            "http://121.165.240.250:3003",
            "https://academy-ai-assistants.vercel.app",
            "https://academy-ai-assistant.vercel.app",
            "https://*.vercel.app",
        ]
        
        if self.environment == "production":
            origins.extend([
                "https://your-domain.com",
                "https://www.your-domain.com",
            ])
        
        return origins
    
    # Debug
    debug: bool = config("DEBUG", default=True, cast=bool)

settings = Settings() 
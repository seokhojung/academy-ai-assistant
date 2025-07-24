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
    
    # AI API 설정
    ai_model: str = str(config("AI_MODEL", default="openai"))  # "gemini" 또는 "openai"
    
    # Gemini API
    gemini_api_key: str = str(config("GEMINI_API_KEY", default=""))
    
    # OpenAI API
    openai_api_key: str = str(config("OPENAI_API_KEY", default=""))
    openai_model: str = str(config("OPENAI_MODEL", default="gpt-3.5-turbo"))
    openai_max_tokens: int = config("OPENAI_MAX_TOKENS", default=2000, cast=int)
    openai_temperature: float = config("OPENAI_TEMPERATURE", default=0.7, cast=float)
    openai_top_p: float = config("OPENAI_TOP_P", default=1.0, cast=float)
    openai_frequency_penalty: float = config("OPENAI_FREQUENCY_PENALTY", default=0.0, cast=float)
    openai_presence_penalty: float = config("OPENAI_PRESENCE_PENALTY", default=0.0, cast=float)
    
    @property
    def is_ai_enabled(self) -> bool:
        """AI 서비스 활성화 여부"""
        if self.ai_model == "gemini":
            return bool(self.gemini_api_key and self.gemini_api_key != "")
        elif self.ai_model == "openai":
            return bool(self.openai_api_key and self.openai_api_key != "")
        return False
    
    @property
    def current_ai_model(self) -> str:
        """현재 사용 중인 AI 모델"""
        return self.ai_model
    
    @property
    def current_ai_config(self) -> dict:
        """현재 AI 서비스 설정"""
        if self.ai_model == "gemini":
            return {
                "model_type": "gemini",
                "api_key": self.gemini_api_key
            }
        elif self.ai_model == "openai":
            return {
                "model_type": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "max_tokens": self.openai_max_tokens,
                "temperature": self.openai_temperature,
                "top_p": self.openai_top_p,
                "frequency_penalty": self.openai_frequency_penalty,
                "presence_penalty": self.openai_presence_penalty
            }
        else:
            return {
                "model_type": "gemini",
                "api_key": self.gemini_api_key
            }
    
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

def get_settings() -> Settings:
    """설정 객체를 반환하는 함수"""
    return settings 
from typing import Dict, Any
from .unified_ai_service import UnifiedAIService
from app.core.config import settings

class AIServiceFactory:
    """AI 서비스 팩토리"""
    
    @classmethod
    def create_service(cls, config: Dict[str, Any], prompt_type: str = "optimized") -> UnifiedAIService:
        """AI 서비스 생성"""
        model_type = config.get("model_type", "openai")
        api_key = config.get("api_key", "")
        
        # config에서 model_type과 api_key 제거 (중복 방지)
        service_config = config.copy()
        service_config.pop("model_type", None)
        service_config.pop("api_key", None)
        
        print(f"[AIServiceFactory] {model_type} 모델로 서비스 생성 (지침: {prompt_type})")
        
        return UnifiedAIService(
            model_type=model_type,
            api_key=api_key,
            prompt_type=prompt_type,
            **service_config
        )
    
    @classmethod
    def create_service_with_original_prompt(cls, config: Dict[str, Any]) -> UnifiedAIService:
        """기존 지침으로 AI 서비스 생성"""
        return cls.create_service(config, "original")
    
    @classmethod
    def create_service_with_optimized_prompt(cls, config: Dict[str, Any]) -> UnifiedAIService:
        """최적화된 지침으로 AI 서비스 생성"""
        return cls.create_service(config, "optimized") 
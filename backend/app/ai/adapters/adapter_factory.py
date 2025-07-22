from typing import Dict, Any, List
from .base_adapter import BaseAIAdapter
from .gemini_adapter import GeminiAdapter
from .openai_adapter import OpenAIAdapter

class AdapterFactory:
    """AI 어댑터 팩토리"""
    
    _adapters = {
        "gemini": GeminiAdapter,
        "openai": OpenAIAdapter
    }
    
    @classmethod
    def create_adapter(cls, model_type: str, api_key: str, **kwargs) -> BaseAIAdapter:
        """어댑터 생성"""
        if model_type not in cls._adapters:
            raise ValueError(f"지원하지 않는 모델: {model_type}")
        
        adapter_class = cls._adapters[model_type]
        return adapter_class(api_key, **kwargs)
    
    @classmethod
    def get_supported_models(cls) -> List[str]:
        """지원하는 모델 목록 반환"""
        return list(cls._adapters.keys()) 
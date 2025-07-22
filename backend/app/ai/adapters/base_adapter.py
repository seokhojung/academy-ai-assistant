from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlmodel import Session

class BaseAIAdapter(ABC):
    """AI 어댑터 기본 인터페이스"""
    
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.kwargs = kwargs
        self._initialize_model()
    
    @abstractmethod
    def _initialize_model(self):
        """모델 초기화"""
        pass
    
    @abstractmethod
    def format_prompt(self, system_prompt: str, context_data: Dict[str, Any], user_message: str) -> Any:
        """모델별 프롬프트 포맷팅"""
        pass
    
    @abstractmethod
    async def generate_response(self, formatted_prompt: Any) -> str:
        """AI 응답 생성"""
        pass
    
    @abstractmethod
    def parse_response(self, raw_response: Any) -> str:
        """모델별 응답 파싱"""
        pass
    
    def optimize_prompt(self, prompt: str) -> str:
        """모델별 프롬프트 최적화"""
        return prompt 
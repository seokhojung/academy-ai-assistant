import google.generativeai as genai
from .base_adapter import BaseAIAdapter
from typing import Dict, Any

class GeminiAdapter(BaseAIAdapter):
    """Gemini AI 어댑터"""
    
    def _initialize_model(self):
        """Gemini 모델 초기화"""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def format_prompt(self, system_prompt: str, context_data: Dict[str, Any], user_message: str) -> str:
        """Gemini용 프롬프트 포맷팅"""
        return f"""
        {system_prompt}
        
        ## 사용자 질문
        {user_message}
        """
    
    async def generate_response(self, formatted_prompt: str) -> str:
        """Gemini 응답 생성"""
        response = self.model.generate_content(formatted_prompt)
        return response.text if response.text else ""
    
    def parse_response(self, raw_response) -> str:
        """Gemini 응답 파싱"""
        return raw_response.text if raw_response.text else ""
    
    def optimize_prompt(self, prompt: str) -> str:
        """Gemini 특화 프롬프트 최적화"""
        return prompt + "\n\n## 🚨 Gemini 특화 지침\n- 상세한 지침을 정확히 따르세요" 
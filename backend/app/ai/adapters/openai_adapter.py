from openai import OpenAI
from .base_adapter import BaseAIAdapter
from typing import Dict, Any, List, Optional
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class OpenAIAdapter(BaseAIAdapter):
    """OpenAI AI 어댑터 - 최적화된 버전"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self._initialize_model()
    
    def _initialize_model(self):
        """OpenAI 모델 초기화"""
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.model = self.kwargs.get("model", "gpt-3.5-turbo")
            self.max_tokens = self.kwargs.get("max_tokens", 2000)
            self.temperature = self.kwargs.get("temperature", 0.7)
            self.top_p = self.kwargs.get("top_p", 1.0)
            self.frequency_penalty = self.kwargs.get("frequency_penalty", 0.0)
            self.presence_penalty = self.kwargs.get("presence_penalty", 0.0)
            
            logger.info(f"OpenAI 어댑터 초기화 완료: {self.model}")
        except Exception as e:
            logger.error(f"OpenAI 어댑터 초기화 실패: {e}")
            raise
    
    def format_prompt(self, system_prompt: str, context_data: Dict[str, Any], user_message: str) -> List[Dict[str, str]]:
        """OpenAI용 프롬프트 포맷팅 (messages 형식)"""
        try:
            # 컨텍스트 데이터를 JSON 문자열로 변환
            context_str = json.dumps(context_data, ensure_ascii=False, indent=2)
            
            # 시스템 프롬프트에 컨텍스트 포함
            enhanced_system_prompt = f"""
{system_prompt}

## 📊 현재 데이터베이스 컨텍스트
```json
{context_str}
```

## 🎯 응답 요구사항
- 반드시 JSON 형식으로 응답
- 한국어로 응답
- 실제 데이터만 사용
- HTML 태그 사용 금지
"""
            
            return [
                {"role": "system", "content": enhanced_system_prompt.strip()},
                {"role": "user", "content": user_message}
            ]
        except Exception as e:
            logger.error(f"프롬프트 포맷팅 실패: {e}")
            # 기본 형식으로 폴백
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
    
    async def generate_response(self, formatted_prompt: List[Dict[str, str]]) -> str:
        """OpenAI 응답 생성 (최적화된 버전)"""
        try:
            # JSON 형식 강제를 위한 추가 설정
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=formatted_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                response_format={"type": "json_object"},  # JSON 형식 강제
                seed=42  # 일관된 응답을 위한 시드 설정
            )
            
            content = response.choices[0].message.content if response.choices else ""
            logger.info(f"OpenAI 응답 생성 성공: {len(content)} 문자")
            
            # JSON 형식 검증 및 수정
            try:
                json.loads(content)
                return content
            except json.JSONDecodeError:
                logger.warning("OpenAI 응답이 JSON 형식이 아님, 기본 JSON 형식으로 변환")
                # 기본 JSON 형식으로 변환
                return json.dumps({
                    "type": "text",
                    "content": content,
                    "error": "원본 응답이 JSON 형식이 아니었습니다"
                }, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"OpenAI 응답 생성 실패: {e}")
            # 에러 시 기본 JSON 형식 반환
            return json.dumps({
                "type": "error",
                "content": f"OpenAI API 오류: {str(e)}",
                "error": True
            }, ensure_ascii=False)
    
    def parse_response(self, raw_response) -> str:
        """OpenAI 응답 파싱 (향상된 버전)"""
        try:
            # raw_response가 이미 문자열인 경우 (우리 시스템에서 발생하는 경우)
            if isinstance(raw_response, str):
                # JSON 구조 수정: table_data로 감싸진 경우 제거
                try:
                    parsed = json.loads(raw_response)
                    if "table_data" in parsed and isinstance(parsed["table_data"], dict):
                        # table_data로 감싸진 경우 내부 내용만 반환
                        logger.info("table_data 래퍼 제거됨")
                        return json.dumps(parsed["table_data"], ensure_ascii=False)
                    return raw_response
                except json.JSONDecodeError:
                    return raw_response
            
            # raw_response가 OpenAI 응답 객체인 경우
            if hasattr(raw_response, 'choices') and raw_response.choices:
                content = raw_response.choices[0].message.content
                
                # JSON 형식 검증 및 구조 수정
                try:
                    parsed = json.loads(content)
                    print(f"[OpenAI Adapter] 원본 응답: {parsed}")
                    
                    if "table_data" in parsed and isinstance(parsed["table_data"], dict):
                        # table_data로 감싸진 경우 내부 내용만 반환
                        logger.info("table_data 래퍼 제거됨")
                        result = json.dumps(parsed["table_data"], ensure_ascii=False)
                        print(f"[OpenAI Adapter] 수정된 응답: {result}")
                        return result
                    
                    # 올바른 구조인지 확인
                    if "type" in parsed and "content" in parsed:
                        logger.info("올바른 구조 확인됨")
                        return content
                    
                    return content
                except json.JSONDecodeError:
                    logger.warning("응답이 JSON 형식이 아님, 기본 형식으로 반환")
                    return content
            
            return ""
        except Exception as e:
            logger.error(f"응답 파싱 실패: {e}")
            return ""
    
    def optimize_prompt(self, prompt: str) -> str:
        """OpenAI 특화 프롬프트 최적화 (향상된 버전)"""
        optimized_prompt = f"""
{prompt}

## 🚨 OpenAI 특화 지침
- 반드시 JSON 형식으로 응답해주세요
- 한국어로 응답해주세요
- 실제 데이터베이스의 데이터만 사용해주세요
- HTML 태그나 마크다운 형식을 사용하지 마세요
- 응답은 항상 유효한 JSON 객체여야 합니다
- 배열이나 객체의 경우 적절한 구조로 응답해주세요

## 📝 응답 형식 예시
```json
{{
  "type": "text",
  "content": "응답 내용",
  "data": {{}},
  "actions": []
}}
```
"""
        return optimized_prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        return {
            "provider": "openai",
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "features": ["json_response", "context_aware", "korean_support"]
        }
    
    async def test_connection(self) -> bool:
        """연결 테스트"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": "테스트"}],
                max_tokens=10
            )
            return bool(response.choices)
        except Exception as e:
            logger.error(f"OpenAI 연결 테스트 실패: {e}")
            return False 
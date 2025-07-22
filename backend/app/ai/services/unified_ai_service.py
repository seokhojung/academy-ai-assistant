from typing import Dict, Any, Optional
from sqlmodel import Session
from ..core.base_prompt import BasePrompt
from ..core.prompt_factory import PromptFactory
from ..core.context_builder import ContextBuilder
from ..core.response_validator import ResponseValidator
from ..adapters.adapter_factory import AdapterFactory
import json

class UnifiedAIService:
    """통합 AI 서비스 (모델 무관)"""
    
    def __init__(self, model_type: str, api_key: str, prompt_type: str = "optimized", **kwargs):
        self.adapter = AdapterFactory.create_adapter(model_type, api_key, **kwargs)
        self.prompt_manager = PromptFactory.create_prompt(prompt_type)
        self.context_builder = ContextBuilder()
        self.validator = ResponseValidator()
        self.max_retries = 3
        self.prompt_type = prompt_type
        
        print(f"[UnifiedAIService] {prompt_type} 지침으로 초기화됨")
    
    def switch_prompt_type(self, prompt_type: str):
        """지침 타입 변경"""
        self.prompt_manager = PromptFactory.create_prompt(prompt_type)
        self.prompt_type = prompt_type
        print(f"[UnifiedAIService] 지침 타입 변경: {prompt_type}")
    
    def get_current_prompt_info(self) -> Dict[str, str]:
        """현재 사용 중인 지침 정보 반환"""
        available_prompts = PromptFactory.get_available_prompts()
        if self.prompt_type in available_prompts:
            return {
                "type": self.prompt_type,
                "name": available_prompts[self.prompt_type]["name"],
                "description": available_prompts[self.prompt_type]["description"]
            }
        return {"type": "unknown", "name": "알 수 없음", "description": "알 수 없음"}
    
    def get_prompt_comparison(self) -> str:
        """지침 비교 리포트 반환"""
        return PromptFactory.compare_prompts()
    
    async def generate_response(
        self, 
        message: str, 
        session: Optional[Session] = None
    ) -> str:
        """AI 응답 생성 (검증 포함)"""
        
        # CRUD 명령 감지
        if self._is_crud_request(message):
            print(f"[UnifiedAIService] CRUD 요청 감지: {message}")
            return await self._handle_crud_request(message, session)
        
        for attempt in range(self.max_retries):
            try:
                print(f"[UnifiedAIService] 시도 {attempt + 1} 시작")
                
                # 1. 컨텍스트 데이터 구축
                context_data = await self.context_builder.build_context(session)
                filtered_context = self.context_builder.filter_context_by_keywords(context_data, message)
                print(f"[UnifiedAIService] 컨텍스트 구축 완료: {len(filtered_context)} 항목")
                
                # 2. 프롬프트 생성
                system_prompt = self.prompt_manager.get_full_prompt(filtered_context, message)
                optimized_prompt = self.adapter.optimize_prompt(system_prompt)
                print(f"[UnifiedAIService] 프롬프트 생성 완료: {len(optimized_prompt)} 문자")
                
                # 3. 모델별 프롬프트 포맷팅
                formatted_prompt = self.adapter.format_prompt(optimized_prompt, filtered_context, message)
                print(f"[UnifiedAIService] 프롬프트 포맷팅 완료: {len(formatted_prompt)} 메시지")
                
                # 4. AI 응답 생성
                print(f"[UnifiedAIService] AI 응답 생성 시작...")
                raw_response = await self.adapter.generate_response(formatted_prompt)
                print(f"[UnifiedAIService] AI 응답 생성 완료: {len(raw_response)} 문자")
                print(f"[UnifiedAIService] AI 원본 응답: {raw_response[:200]}...")
                
                response = self.adapter.parse_response(raw_response)
                print(f"[UnifiedAIService] 응답 파싱 완료: {len(response)} 문자")
                
                # 5. 응답 검증
                is_valid, error_message = self.validator.validate_response(response, context_data)
                
                if is_valid:
                    print(f"[UnifiedAIService] 응답 검증 성공 (시도 {attempt + 1})")
                    return response
                else:
                    print(f"[UnifiedAIService] 응답 검증 실패 (시도 {attempt + 1}): {error_message}")
                    
                    # 마지막 시도가 아니면 더 강한 프롬프트로 재시도
                    if attempt < self.max_retries - 1:
                        system_prompt = self._get_stronger_prompt(filtered_context, message, error_message)
                        continue
                    else:
                        return self._get_fallback_response(message, error_message)
                        
            except Exception as e:
                print(f"[UnifiedAIService] 오류 발생 (시도 {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return f"AI 서비스 오류가 발생했습니다: {str(e)}"
        
        return "죄송합니다. 응답을 생성할 수 없습니다."
    
    async def generate_response_stream(
        self, 
        message: str, 
        session: Optional[Session] = None
    ):
        """AI 스트리밍 응답 생성"""
        try:
            print(f"[UnifiedAIService] 스트리밍 응답 시작")
            
            # 1. 컨텍스트 데이터 구축
            context_data = await self.context_builder.build_context(session)
            filtered_context = self.context_builder.filter_context_by_keywords(context_data, message)
            print(f"[UnifiedAIService] 스트리밍 컨텍스트 구축 완료: {len(filtered_context)} 항목")
            
            # 2. 프롬프트 생성
            system_prompt = self.prompt_manager.get_full_prompt(filtered_context, message)
            optimized_prompt = self.adapter.optimize_prompt(system_prompt)
            
            # 3. 모델별 프롬프트 포맷팅
            formatted_prompt = self.adapter.format_prompt(optimized_prompt, filtered_context, message)
            
            # 4. AI 스트리밍 응답 생성
            print(f"[UnifiedAIService] AI 스트리밍 응답 생성 시작...")
            async for chunk in self.adapter.generate_response_stream(formatted_prompt):
                yield chunk
                
        except Exception as e:
            print(f"[UnifiedAIService] 스트리밍 오류: {e}")
            yield f"AI 서비스 오류가 발생했습니다: {str(e)}"
    
    def _is_crud_request(self, message: str) -> bool:
        """CRUD 명령어인지 확인합니다."""
        crud_keywords = [
            # 영어 키워드
            "create", "read", "update", "delete", "add", "remove", "modify", "edit",
            # 한국어 키워드
            "생성", "추가", "등록", "만들", "조회", "보기", "확인", "수정", "변경", "편집", "삭제", "제거", "지우"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in crud_keywords)
    
    async def _handle_crud_request(self, message: str, session: Optional[Session]) -> str:
        """CRUD 명령어에 대한 처리를 수행합니다."""
        print(f"[UnifiedAIService] CRUD 요청 처리 시작: {message}")
        
        try:
            # 명령어 추출
            command = message.lower()
            if "create" in command:
                print(f"[UnifiedAIService] CRUD: Create 명령어 감지")
                # 예시: 새로운 데이터 생성 로직
                # 이 부분은 실제 데이터베이스 처리 로직으로 대체되어야 합니다.
                # 예: session.add(new_data)
                # session.commit()
                return json.dumps({
                    "type": "text",
                    "content": f"Create 명령어를 처리했습니다. 데이터: {message}"
                }, ensure_ascii=False)
            elif "read" in command:
                print(f"[UnifiedAIService] CRUD: Read 명령어 감지")
                # 예시: 데이터 조회 로직
                # 이 부분은 실제 데이터베이스 처리 로직으로 대체되어야 합니다.
                # 예: session.query(DataModel).all()
                return json.dumps({
                    "type": "text",
                    "content": f"Read 명령어를 처리했습니다. 데이터: {message}"
                }, ensure_ascii=False)
            elif "update" in command:
                print(f"[UnifiedAIService] CRUD: Update 명령어 감지")
                # 예시: 데이터 업데이트 로직
                # 이 부분은 실제 데이터베이스 처리 로직으로 대체되어야 합니다.
                # 예: session.query(DataModel).filter(DataModel.id == 1).update(new_data)
                # session.commit()
                return json.dumps({
                    "type": "text",
                    "content": f"Update 명령어를 처리했습니다. 데이터: {message}"
                }, ensure_ascii=False)
            elif "delete" in command:
                print(f"[UnifiedAIService] CRUD: Delete 명령어 감지")
                # 예시: 데이터 삭제 로직
                # 이 부분은 실제 데이터베이스 처리 로직으로 대체되어야 합니다.
                # 예: session.query(DataModel).filter(DataModel.id == 1).delete()
                # session.commit()
                return json.dumps({
                    "type": "text",
                    "content": f"Delete 명령어를 처리했습니다. 데이터: {message}"
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "type": "text",
                    "content": f"알 수 없는 CRUD 명령어입니다: {message}"
                }, ensure_ascii=False)
        except Exception as e:
            print(f"[UnifiedAIService] CRUD 요청 처리 중 오류 발생: {e}")
            return json.dumps({
                "type": "text",
                "content": f"CRUD 요청 처리 중 오류가 발생했습니다: {str(e)}"
            }, ensure_ascii=False)
    
    def _get_stronger_prompt(self, context_data: Dict[str, Any], message: str, error_message: str) -> str:
        """더 강한 프롬프트 생성"""
        return f"""
        {self.prompt_manager.get_full_prompt(context_data, message)}
        
        ## 🚨 이전 응답 오류 수정 요청
        오류: {error_message}
        
        위 오류를 수정하여 정확한 JSON 형식으로 응답해주세요.
        """
    
    def _get_fallback_response(self, message: str, error_message: str) -> str:
        """폴백 응답 생성"""
        return json.dumps({
            "type": "text",
            "content": f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {error_message}"
        }, ensure_ascii=False) 
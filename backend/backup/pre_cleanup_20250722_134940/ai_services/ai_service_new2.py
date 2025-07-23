from abc import ABC, abstractmethod
from typing import Optional, AsyncGenerator, Dict, Any
from sqlmodel import Session
import json
import asyncio
import google.generativeai as genai
from app.core.config import settings
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.material import Material
from app.models.lecture import Lecture
from app.services.openai_service import OpenAIService

class AIService(ABC):
    @abstractmethod
    async def generate_response(self, message: str, session: Optional[Session] = None) -> str:
        pass
    
    @abstractmethod
    async def generate_stream(self, message: str) -> AsyncGenerator[str, None]:
        pass

class GeminiService(AIService):
    def __init__(self):
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print(f"[AI] Gemini 서비스 초기화 성공")
        except Exception as e:
            print(f"[AI] Gemini 서비스 초기화 실패: {e}")
            raise
    
    async def generate_response(self, message: str, session: Optional[Session] = None) -> str:
        """Gemini API를 사용한 응답 생성"""
        try:
            # 데이터베이스에서 최신 정보 가져오기
            context_data = await self._get_context_data(session)
            
            # 시스템 프롬프트 구성
            system_prompt = self._build_system_prompt(context_data)
            
            # Gemini API 호출
            response = self.model.generate_content(
                system_prompt + "\n\n사용자: " + message,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.7
                )
            )
            
            if response.text:
                return response.text
            else:
                return "죄송합니다. 응답을 생성할 수 없습니다."
                
        except Exception as e:
            print(f"[AI] Gemini API 오류: {e}")
            return f"AI 서비스 오류가 발생했습니다: {str(e)}"
    
    async def generate_stream(self, message: str) -> AsyncGenerator[str, None]:
        """Gemini API를 사용한 스트리밍 응답 생성"""
        try:
            system_prompt = self._build_system_prompt({})
            full_prompt = system_prompt + "\n\n사용자: " + message
            
            response = self.model.generate_content(
                full_prompt,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.7
                )
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            yield f"AI 서비스 오류가 발생했습니다: {str(e)}"
    
    async def _get_context_data(self, session: Optional[Session]) -> Dict[str, Any]:
        """데이터베이스에서 컨텍스트 데이터 가져오기"""
        context_data = {}
        if session:
            try:
                # 학생 정보
                students = session.query(Student).all()
                students = sorted(students, key=lambda x: x.created_at, reverse=True)
                context_data['students'] = [
                    {
                        'name': s.name,
                        'grade': s.grade,
                        'email': s.email,
                        'phone': s.phone,
                        'tuition_fee': s.tuition_fee,
                        'is_active': s.is_active
                    } for s in students
                ]
                
                # 강사 정보
                teachers = session.query(Teacher).all()
                teachers = sorted(teachers, key=lambda x: x.created_at, reverse=True)
                context_data['teachers'] = [
                    {
                        'name': t.name,
                        'subject': t.subject,
                        'email': t.email,
                        'phone': t.phone,
                        'hourly_rate': t.hourly_rate,
                        'is_active': t.is_active
                    } for t in teachers
                ]
                
                # 교재 정보
                materials = session.query(Material).all()
                materials = sorted(materials, key=lambda x: x.created_at, reverse=True)
                context_data['materials'] = [
                    {
                        'name': m.name,
                        'subject': m.subject,
                        'grade': m.grade,
                        'publisher': m.publisher,
                        'quantity': m.quantity,
                        'price': m.price,
                        'is_active': m.is_active
                    } for m in materials
                ]
                
                # 강의 정보
                lectures = session.query(Lecture).all()
                lectures = sorted(lectures, key=lambda x: x.created_at, reverse=True)
                context_data['lectures'] = [
                    {
                        'title': l.title,
                        'subject': l.subject,
                        'grade': l.grade,
                        'schedule': l.schedule,
                        'classroom': l.classroom,
                        'max_students': l.max_students,
                        'current_students': l.current_students,
                        'tuition_fee': l.tuition_fee,
                        'is_active': l.is_active
                    } for l in lectures
                ]
                
            except Exception as db_error:
                print(f"[AI] 데이터베이스 조회 오류: {db_error}")
                context_data = {}
        
        return context_data
    
    def _build_system_prompt(self, context_data: Dict[str, Any]) -> str:
        """시스템 프롬프트 구성 (OpenAI와 동일한 수준으로 향상)"""
        prompt = """당신은 학원 관리 시스템의 AI 어시스턴트입니다. 학생, 강사, 교재, 강의 정보를 관리하고 질문에 답변합니다.

응답 형식:
1. 일반 질문: 자연스러운 한국어로 답변
2. 데이터 조회: JSON 형식의 table_data로 응답
3. CRUD 명령: JSON 형식의 crud_command로 응답

현재 시스템 데이터:"""

        if context_data:
            student_count = len(context_data.get('students', []))
            teacher_count = len(context_data.get('teachers', []))
            material_count = len(context_data.get('materials', []))
            lecture_count = len(context_data.get('lectures', []))
            
            prompt += f"""
- 학생: {student_count}명
- 강사: {teacher_count}명  
- 교재: {material_count}개
- 강의: {lecture_count}개

실제 데이터:
"""
            
            # 실제 데이터 포함 (OpenAI와 동일)
            if context_data.get('lectures'):
                prompt += "\n강의 목록:\n"
                for i, lecture in enumerate(context_data['lectures'][:10], 1):
                    prompt += f"{i}. {lecture['title']} ({lecture['subject']}, {lecture['grade']})\n"
            
            if context_data.get('students'):
                prompt += "\n학생 목록 (일부):\n"
                for i, student in enumerate(context_data['students'][:5], 1):
                    prompt += f"{i}. {student['name']} ({student['grade']})\n"
                    
        else:
            prompt += "\n- 데이터베이스 연결 없음"
        
        prompt += """

응답 형식 규칙:
- 데이터 조회 요청 (강의 목록, 학생 목록, 교재 목록 등) → 반드시 JSON 형식의 table_data로 응답
- 데이터 수정 요청 (추가, 수정, 삭제) → 반드시 JSON 형식의 crud_command로 응답
- 일반 질문 → 자연스러운 한국어로 답변

테이블 데이터 응답 형식 (데이터 조회 시 필수):
{
  "type": "table_data",
  "content": {
    "title": "강의 목록",
    "headers": ["강의명", "과목", "학년", "수강료"],
    "rows": [
      ["고등수학 기초반", "수학", "고등학교 1학년", "150,000원"],
      ["중등영어 심화반", "영어", "중학교 3학년", "120,000원"]
    ],
    "footer": "총 11개 강의"
  }
}

CRUD 명령 응답 형식 (데이터 수정 시 필수):
{
  "type": "crud_command",
  "content": {
    "action": "create|update|delete",
    "entity": "student|teacher|material|lecture",
    "target": {"identifier": "이름 또는 ID"},
    "data": {"수정할_필드": "값"},
    "confirmation": "사용자에게 확인할 메시지",
    "requires_confirmation": true
  }
}

중요 지시사항: 
1. "강의 목록 보여줘", "학생 목록", "교재 목록" 등의 데이터 조회 요청 → 반드시 JSON 형식의 table_data로 응답
2. "강의 추가", "학생 수정", "교재 삭제" 등의 데이터 수정 요청 → 반드시 JSON 형식의 crud_command로 응답
3. 실제 데이터베이스의 정보를 기반으로 정확한 답변을 제공하세요.
4. JSON 응답 시에는 반드시 위의 형식을 정확히 따라주세요.
5. 항상 한국어로 응답하고, 명확하고 도움이 되는 답변을 제공하세요."""
        
        return prompt

class OpenAIService(AIService):
    def __init__(self):
        try:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
            print(f"[AI] OpenAI 서비스 초기화 성공 (모델: {self.model})")
        except Exception as e:
            print(f"[AI] OpenAI 서비스 초기화 실패: {e}")
            raise
    
    async def generate_response(self, message: str, session: Optional[Session] = None) -> str:
        """OpenAI API를 사용한 응답 생성 (Gemini 수준으로 향상)"""
        try:
            print(f"[AI] OpenAI API 호출 시작: {message[:30]}...")
            
            # 데이터베이스에서 최신 정보 가져오기
            context_data = await self._get_context_data(session)
            print(f"[AI] 컨텍스트 데이터 로드: {len(context_data)}개 항목")
            
            # 시스템 프롬프트 구성 (Gemini와 동일한 수준)
            system_prompt = self._build_system_prompt(context_data)
            print(f"[AI] 시스템 프롬프트 길이: {len(system_prompt)}자")
            
            # OpenAI API 호출 (Gemini 수준으로 향상)
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,  # Gemini와 동일한 토큰 제한
                temperature=0.7,
                presence_penalty=0.1,  # 반복 방지
                frequency_penalty=0.1   # 다양성 증가
            )
            
            print(f"[AI] OpenAI API 응답 받음")
            
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content
            else:
                return "죄송합니다. 응답을 생성할 수 없습니다."
                
        except Exception as e:
            print(f"[AI] OpenAI API 오류: {e}")
            return f"AI 서비스 오류가 발생했습니다: {str(e)}"
    
    async def generate_stream(self, message: str) -> AsyncGenerator[str, None]:
        """OpenAI API를 사용한 스트리밍 응답 생성"""
        try:
            system_prompt = self._build_system_prompt({})
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,
                temperature=0.7,
                stream=True,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"AI 서비스 오류가 발생했습니다: {str(e)}"
    
    async def _get_context_data(self, session: Optional[Session]) -> Dict[str, Any]:
        """데이터베이스에서 컨텍스트 데이터 가져오기 (Gemini와 동일)"""
        context_data = {}
        if session:
            try:
                print(f"[AI] 데이터베이스 조회 시작...")
                
                # 학생 정보
                students = session.query(Student).all()
                students = sorted(students, key=lambda x: x.created_at, reverse=True)
                context_data['students'] = [
                    {
                        'name': s.name,
                        'grade': s.grade,
                        'email': s.email,
                        'phone': s.phone,
                        'tuition_fee': s.tuition_fee,
                        'is_active': s.is_active
                    } for s in students
                ]
                print(f"[AI] 학생 데이터 조회: {len(context_data['students'])}명")
                
                # 강사 정보
                teachers = session.query(Teacher).all()
                teachers = sorted(teachers, key=lambda x: x.created_at, reverse=True)
                context_data['teachers'] = [
                    {
                        'name': t.name,
                        'subject': t.subject,
                        'email': t.email,
                        'phone': t.phone,
                        'hourly_rate': t.hourly_rate,
                        'is_active': t.is_active
                    } for t in teachers
                ]
                print(f"[AI] 강사 데이터 조회: {len(context_data['teachers'])}명")
                
                # 교재 정보
                materials = session.query(Material).all()
                materials = sorted(materials, key=lambda x: x.created_at, reverse=True)
                context_data['materials'] = [
                    {
                        'name': m.name,
                        'subject': m.subject,
                        'grade': m.grade,
                        'publisher': m.publisher,
                        'quantity': m.quantity,
                        'price': m.price,
                        'is_active': m.is_active
                    } for m in materials
                ]
                print(f"[AI] 교재 데이터 조회: {len(context_data['materials'])}개")
                
                # 강의 정보
                lectures = session.query(Lecture).all()
                lectures = sorted(lectures, key=lambda x: x.created_at, reverse=True)
                context_data['lectures'] = [
                    {
                        'title': l.title,
                        'subject': l.subject,
                        'grade': l.grade,
                        'schedule': l.schedule,
                        'classroom': l.classroom,
                        'max_students': l.max_students,
                        'current_students': l.current_students,
                        'tuition_fee': l.tuition_fee,
                        'is_active': l.is_active
                    } for l in lectures
                ]
                print(f"[AI] 강의 데이터 조회: {len(context_data['lectures'])}개")
                
                print(f"[AI] 데이터베이스 조회 완료")
                
            except Exception as db_error:
                print(f"[AI] 데이터베이스 조회 오류: {db_error}")
                context_data = {}
        else:
            print(f"[AI] 세션이 없어서 데이터베이스 조회 불가")
        
        return context_data
    
    def _build_system_prompt(self, context_data: Dict[str, Any]) -> str:
        """시스템 프롬프트 구성 (OpenAI와 동일한 수준으로 향상)"""
        prompt = """당신은 학원 관리 시스템의 AI 어시스턴트입니다. 학생, 강사, 교재, 강의 정보를 관리하고 질문에 답변합니다.

응답 형식:
1. 일반 질문: 자연스러운 한국어로 답변
2. 데이터 조회: JSON 형식의 table_data로 응답
3. CRUD 명령: JSON 형식의 crud_command로 응답

현재 시스템 데이터:"""

        if context_data:
            student_count = len(context_data.get('students', []))
            teacher_count = len(context_data.get('teachers', []))
            material_count = len(context_data.get('materials', []))
            lecture_count = len(context_data.get('lectures', []))
            
            prompt += f"""
- 학생: {student_count}명
- 강사: {teacher_count}명  
- 교재: {material_count}개
- 강의: {lecture_count}개

실제 데이터:
"""
            
            # 실제 데이터 포함 (OpenAI와 동일)
            if context_data.get('lectures'):
                prompt += "\n강의 목록:\n"
                for i, lecture in enumerate(context_data['lectures'][:10], 1):
                    prompt += f"{i}. {lecture['title']} ({lecture['subject']}, {lecture['grade']})\n"
            
            if context_data.get('students'):
                prompt += "\n학생 목록 (일부):\n"
                for i, student in enumerate(context_data['students'][:5], 1):
                    prompt += f"{i}. {student['name']} ({student['grade']})\n"
                    
        else:
            prompt += "\n- 데이터베이스 연결 없음"
        
        prompt += """

응답 형식 규칙:
- 데이터 조회 요청 (강의 목록, 학생 목록, 교재 목록 등) → 반드시 JSON 형식의 table_data로 응답
- 데이터 수정 요청 (추가, 수정, 삭제) → 반드시 JSON 형식의 crud_command로 응답
- 일반 질문 → 자연스러운 한국어로 답변

테이블 데이터 응답 형식 (데이터 조회 시 필수):
{
  "type": "table_data",
  "content": {
    "title": "강의 목록",
    "headers": ["강의명", "과목", "학년", "수강료"],
    "rows": [
      ["고등수학 기초반", "수학", "고등학교 1학년", "150,000원"],
      ["중등영어 심화반", "영어", "중학교 3학년", "120,000원"]
    ],
    "footer": "총 11개 강의"
  }
}

CRUD 명령 응답 형식 (데이터 수정 시 필수):
{
  "type": "crud_command",
  "content": {
    "action": "create|update|delete",
    "entity": "student|teacher|material|lecture",
    "target": {"identifier": "이름 또는 ID"},
    "data": {"수정할_필드": "값"},
    "confirmation": "사용자에게 확인할 메시지",
    "requires_confirmation": true
  }
}

중요 지시사항: 
1. "강의 목록 보여줘", "학생 목록", "교재 목록" 등의 데이터 조회 요청 → 반드시 JSON 형식의 table_data로 응답
2. "강의 추가", "학생 수정", "교재 삭제" 등의 데이터 수정 요청 → 반드시 JSON 형식의 crud_command로 응답
3. 실제 데이터베이스의 정보를 기반으로 정확한 답변을 제공하세요.
4. JSON 응답 시에는 반드시 위의 형식을 정확히 따라주세요.
5. 항상 한국어로 응답하고, 명확하고 도움이 되는 답변을 제공하세요."""
        
        return prompt

def get_ai_service() -> AIService:
    """환경 설정에 따라 적절한 AI 서비스 반환"""
    try:
        print(f"[AI] AI 모델 설정: {settings.current_ai_model}")
        print(f"[AI] AI 서비스 활성화: {settings.is_ai_enabled}")
        
        if not settings.is_ai_enabled:
            raise Exception(f"{settings.current_ai_model.upper()} API 키가 설정되지 않았습니다.")
        
        if settings.current_ai_model == "openai":
            print(f"[AI] OpenAI 서비스 생성 중...")
            return OpenAIService()
        else:
            print(f"[AI] Gemini 서비스 생성 중...")
            return GeminiService()
            
    except Exception as e:
        print(f"[AI] AI 서비스 생성 실패: {e}")
        raise 
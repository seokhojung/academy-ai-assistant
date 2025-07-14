from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from typing import Dict, Any, Optional
import asyncio
import json
import google.generativeai as genai
from app.core.database import get_session
from app.core.auth import AuthService
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()

# Gemini API 설정
genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

async def call_gemini_api(message: str) -> str:
    """Gemini API 호출 (실제 구현)"""
    try:
        # 시스템 프롬프트(역할/권한/개인정보 제한 없음) 추가
        system_prompt = """
        너는 학원 관리 시스템의 관리자 전용 AI 어시스턴트다.
        이 시스템은 내부 관리자만 접근 가능하며, 학생/강사/교재 등 모든 데이터를 자유롭게 조회/수정/삭제할 수 있다.
        개인정보 보호는 외부 노출에만 해당되며, 내부 요청에는 제한을 두지 않는다.
        관리자 요청에는 학생 목록, 강사 목록, 교재 정보 등 모든 데이터를 상세하게 제공해야 한다.
        """
        prompt = f"""
        {system_prompt}
        사용자의 질문: {message}

        답변 형식:
        1. 질문에 대한 직접적인 답변
        2. 추가적인 도움말이나 제안사항
        3. 관련된 시스템 기능 안내
        """
        # Gemini API 호출
        response = model.generate_content(prompt)
        if response.text:
            return response.text
        else:
            return "죄송합니다. 현재 응답을 생성할 수 없습니다."
    except Exception as e:
        print(f"Gemini API 호출 오류: {e}")
        return f"AI 서비스 오류가 발생했습니다: {str(e)}"

async def call_gemini_api_stream(message: str):
    """Gemini API 스트리밍 호출"""
    try:
        # 프롬프트 설정
        prompt = f"""
        당신은 학원 관리 시스템의 AI 어시스턴트입니다.
        사용자의 질문에 대해 친절하고 정확하게 답변해주세요.
        
        사용자 질문: {message}
        
        답변 형식:
        1. 질문에 대한 직접적인 답변
        2. 추가적인 도움말이나 제안사항
        3. 관련된 시스템 기능 안내
        """
        
        # Gemini API 스트리밍 호출
        response = model.generate_content(prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield f"data: {json.dumps({'content': chunk.text})}\n\n"
                await asyncio.sleep(0.1)  # 자연스러운 스트리밍을 위한 지연
                
    except Exception as e:
        print(f"Gemini API 스트리밍 오류: {e}")
        yield f"data: {json.dumps({'error': f'AI 서비스 오류: {str(e)}'})}\n\n"

def generate_temp_response(message: str) -> str:
    """임시 응답 생성 (Gemini API 없이 테스트용)"""
    lower_message = message.lower()
    
    if '학생' in lower_message or 'student' in lower_message:
        return '''학생 관리 기능에 대해 안내드리겠습니다!

📚 주요 기능:
• 학생 등록 및 정보 관리
• 출석 관리 및 통계
• 성적 관리 및 분석
• 수강료 관리

💡 사용 방법:
대시보드에서 "학생 관리" 메뉴를 클릭하시면 학생 목록을 확인할 수 있습니다. 새 학생을 등록하거나 기존 학생 정보를 수정할 수 있습니다.

🔍 추가 도움:
특정 학생에 대한 정보가 필요하시면 "김철수 학생 정보 보여줘"와 같이 말씀해주세요.'''
    
    elif '강사' in lower_message or 'teacher' in lower_message:
        return '''강사 관리 기능에 대해 안내드리겠습니다!

👨‍🏫 주요 기능:
• 강사 등록 및 프로필 관리
• 강의 스케줄 관리
• 강의 현황 및 통계
• 강사별 학생 관리

💡 사용 방법:
대시보드에서 "강사 관리" 메뉴를 클릭하시면 강사 목록을 확인할 수 있습니다. 새 강사를 등록하거나 스케줄을 관리할 수 있습니다.

🔍 추가 도움:
특정 강사의 스케줄이 필요하시면 "이영희 강사 스케줄 확인"과 같이 말씀해주세요.'''
    
    elif '교재' in lower_message or 'material' in lower_message:
        return '''교재 관리 기능에 대해 안내드리겠습니다!

📖 주요 기능:
• 교재 등록 및 정보 관리
• 재고 관리 및 알림
• 교재별 학생 현황
• 교재 사용 통계

💡 사용 방법:
대시보드에서 "교재 관리" 메뉴를 클릭하시면 교재 목록을 확인할 수 있습니다. 새 교재를 등록하거나 재고를 관리할 수 있습니다.

🔍 추가 도움:
특정 교재의 재고가 필요하시면 "수학 교재 재고 확인"과 같이 말씀해주세요.'''
    
    elif '수강료' in lower_message or 'tuition' in lower_message:
        return '''수강료 관리 기능에 대해 안내드리겠습니다!

💰 주요 기능:
• 수강료 납부 현황 관리
• 미납 학생 목록 및 알림
• 납부 일정 관리
• 수강료 통계 및 리포트

💡 사용 방법:
현재 수강료 관리 기능은 개발 중입니다. 곧 학생별 수강료 관리, 납부 현황 추적, 미납 알림 등의 기능을 제공할 예정입니다.

🔍 추가 도움:
미납 학생 목록이 필요하시면 "미납 학생 목록"과 같이 말씀해주세요.'''
    
    elif '안녕' in lower_message or 'hello' in lower_message:
        return '''안녕하세요! 학원 관리 시스템에 오신 것을 환영합니다! 🎉

저는 AI 어시스턴트로서 학원 관리에 필요한 모든 정보를 도와드립니다.

📋 주요 기능:
• 학생 관리 (등록, 정보 수정, 출석 관리)
• 강사 관리 (등록, 스케줄 관리)
• 교재 관리 (등록, 재고 관리)
• 수강료 관리 (납부 현황, 미납 관리)

💬 질문 예시:
- "학생 관리 방법 알려줘"
- "강사 스케줄 확인"
- "교재 재고 현황"
- "미납 학생 목록"

무엇을 도와드릴까요? 😊'''
    
    else:
        return '''안녕하세요! 학원 관리 시스템 AI 어시스턴트입니다. 🤖

현재 다음과 같은 기능에 대해 질문하실 수 있습니다:

📚 학생 관리
👨‍🏫 강사 관리  
📖 교재 관리
💰 수강료 관리

예시 질문:
• "학생 등록 방법 알려줘"
• "강사 스케줄 확인"
• "교재 재고 현황"
• "수강료 납부 현황"

어떤 기능에 대해 궁금하신가요? 😊'''

class ChatRequest(BaseModel):
    message: str

@router.post("/chat", summary="AI 채팅")
async def chat_with_ai(
    message: str = Body(...),
    session: Session = Depends(get_session),
    current_user = Depends(AuthService.get_current_active_user)
):
    """AI와 채팅합니다."""
    try:
        response = await call_gemini_api(message)
        return {"response": response, "user_id": current_user.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 서비스 오류: {str(e)}")

@router.post("/chat/test", summary="AI 채팅 테스트 (인증 없음)")
async def chat_with_ai_test(req: ChatRequest):
    """AI와 채팅합니다. (테스트용, 인증 없음)"""
    try:
        # 환경변수 확인 로그
        key = settings.gemini_api_key
        print(f"[DEBUG] GEMINI_API_KEY: {key[:4]}...{key[-4:]}")
        # Gemini API가 설정되어 있으면 실제 API 호출, 없으면 임시 응답
        if key and key != "your-gemini-api-key":
            response = await call_gemini_api(req.message)
        else:
            response = generate_temp_response(req.message)
        return {"response": response, "status": "success"}
    except Exception as e:
        # 오류 발생 시에도 임시 응답 제공
        return {"response": f"오류: {str(e)}", "status": "error"}

@router.post("/chat/stream", summary="AI 채팅 스트리밍")
async def chat_with_ai_stream(
    message: str = Body(...),
    session: Session = Depends(get_session),
    current_user = Depends(AuthService.get_current_active_user)
):
    """AI와 스트리밍 채팅합니다."""
    return StreamingResponse(
        call_gemini_api_stream(message),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.post("/analyze", summary="학습 분석")
async def analyze_learning(
    data: Dict[str, Any] = Body(...),
    session: Session = Depends(get_session),
    current_user = Depends(AuthService.get_current_active_user)
):
    """학습 데이터를 분석합니다."""
    try:
        # 학습 데이터 분석을 위한 프롬프트
        analysis_prompt = f"""
        다음 학습 데이터를 분석하여 학생의 강점, 약점, 개선 방안을 제시해주세요.
        
        학습 데이터: {json.dumps(data, ensure_ascii=False)}
        
        분석 결과를 다음 형식으로 제공해주세요:
        1. 강점 (strengths): 학생이 잘하는 영역
        2. 약점 (weaknesses): 개선이 필요한 영역
        3. 권장사항 (recommendations): 구체적인 학습 방안
        4. 진행도 점수 (progress_score): 0-100 사이의 점수
        """
        
        # Gemini API로 분석 수행
        response = model.generate_content(analysis_prompt)
        
        if response.text:
            # 응답을 파싱하여 구조화된 데이터로 변환
            try:
                # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
                analysis_text = response.text
                
                # 기본 분석 결과 반환
                analysis_result = {
                    "strengths": ["수학", "과학"],  # 기본값
                    "weaknesses": ["영어"],  # 기본값
                    "recommendations": ["영어 학습 시간을 늘리세요"],  # 기본값
                    "progress_score": 75,  # 기본값
                    "ai_analysis": analysis_text  # AI 분석 텍스트 포함
                }
                
                return analysis_result
            except Exception as parse_error:
                return {
                    "strengths": ["수학", "과학"],
                    "weaknesses": ["영어"],
                    "recommendations": ["영어 학습 시간을 늘리세요"],
                    "progress_score": 75,
                    "ai_analysis": response.text
                }
        else:
            return {
                "strengths": ["수학", "과학"],
                "weaknesses": ["영어"],
                "recommendations": ["영어 학습 시간을 늘리세요"],
                "progress_score": 75,
                "error": "AI 분석 결과를 생성할 수 없습니다."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 오류: {str(e)}")

@router.post("/command", summary="자연어 명령 처리")
async def process_natural_language_command(
    command: str = Body(...),
    session: Session = Depends(get_session),
    current_user = Depends(AuthService.get_current_active_user)
):
    """자연어 명령을 처리합니다."""
    try:
        # 자연어 명령을 구조화된 JSON으로 변환하는 프롬프트
        command_prompt = f"""
        다음 자연어 명령을 JSON 형태로 변환해주세요.
        
        명령: {command}
        
        가능한 명령 유형:
        1. 학생 관련: "김철수 학생 정보 보여줘", "학생 목록 조회"
        2. 강사 관련: "이영희 강사 스케줄 확인", "강사 목록 조회"
        3. 교재 관련: "수학 교재 재고 확인", "교재 목록 조회"
        4. 수강료 관련: "미납 학생 목록", "수강료 납부 현황"
        
        응답 형식:
        {{
            "command_type": "student|teacher|material|tuition",
            "action": "get|create|update|delete|list",
            "target": "student_name|teacher_name|material_name",
            "filters": {{}},
            "parameters": {{}}
        }}
        """
        
        # Gemini API로 명령 파싱
        response = model.generate_content(command_prompt)
        
        if response.text:
            try:
                # JSON 파싱 시도
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    parsed_command = json.loads(json_match.group())
                else:
                    parsed_command = {
                        "command_type": "unknown",
                        "action": "unknown",
                        "target": command,
                        "filters": {},
                        "parameters": {}
                    }
                
                return {
                    "original_command": command,
                    "parsed_command": parsed_command,
                    "ai_response": response.text
                }
            except json.JSONDecodeError:
                return {
                    "original_command": command,
                    "parsed_command": {
                        "command_type": "unknown",
                        "action": "unknown",
                        "target": command,
                        "filters": {},
                        "parameters": {}
                    },
                    "ai_response": response.text
                }
        else:
            return {
                "original_command": command,
                "error": "명령을 파싱할 수 없습니다."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"명령 처리 오류: {str(e)}") 
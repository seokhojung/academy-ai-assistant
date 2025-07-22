from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from typing import Dict, Any, Optional
import asyncio
import json
import google.generativeai as genai
from app.core.database import get_session
from app.core.auth import AuthService
from app.core.config import settings
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.material import Material
from app.models.lecture import Lecture
from pydantic import BaseModel
from app.ai.core.context_builder import ContextBuilder
from app.ai.services.ai_service_factory import AIServiceFactory
from app.ai.core.prompt_factory import PromptFactory

# 새로운 통합 AI 서비스 import
try:
    ai_service = AIServiceFactory.create_service(settings.current_ai_config)
    print("[AI] 새로운 통합 AI 시스템 로드됨")
except Exception as e:
    print(f"[AI] 새로운 AI 시스템 로드 실패: {e}")
    raise Exception(f"AI 시스템 초기화 실패: {e}")

router = APIRouter()

async def call_ai_api(message: str, session: Optional[Session] = None) -> str:
    """AI API 호출 (새로운 ContextBuilder 사용)"""
    try:
        # ContextBuilder를 사용하여 데이터 조회
        context_data = await ContextBuilder.build_context(session)
        print(f"[AI] ContextBuilder에서 조회된 데이터: {list(context_data.keys())}")
        
        # 키워드 기반 필터링
        filtered_context = ContextBuilder.filter_context_by_keywords(context_data, message)
        print(f"[AI] 필터링된 컨텍스트: {list(filtered_context.keys())}")
        
        # AI 서비스를 통해 응답 생성
        response = await ai_service.generate_response(message, session)
        print(f"[AI] AI 응답 생성 완료: {len(response)} 문자")
        
        return response
        
    except Exception as e:
        print(f"[AI] AI API 호출 오류: {e}")
        return f"AI 서비스 오류가 발생했습니다: {str(e)}"

async def call_ai_api_stream(message: str, session: Optional[Session] = None):
    """AI API 스트리밍 호출"""
    try:
        # ContextBuilder를 사용하여 데이터 조회
        context_data = await ContextBuilder.build_context(session)
        filtered_context = ContextBuilder.filter_context_by_keywords(context_data, message)
        
        # AI 서비스를 통해 스트리밍 응답 생성
        async for chunk in ai_service.generate_response_stream(message, session):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
            await asyncio.sleep(0.1)
                
    except Exception as e:
        print(f"[AI] AI API 스트리밍 오류: {e}")
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
        response = await call_ai_api(message, session)
        return {"response": response, "user_id": current_user.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 서비스 오류: {str(e)}")

@router.post("/chat/test", summary="AI 채팅 테스트 (인증 없음)")
async def chat_with_ai_test(req: ChatRequest, session: Session = Depends(get_session)):
    """AI와 채팅합니다. (테스트용, 인증 없음)"""
    try:
        # 새로운 통합 AI 서비스 사용
        response = await call_ai_api(req.message, session)
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
        call_ai_api_stream(message, session),
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
        
        # AI API로 분석 수행
        response = await ai_service.generate_response(analysis_prompt, session)
        
        if response:
            # 응답을 파싱하여 구조화된 데이터로 변환
            try:
                # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
                analysis_text = response
                
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
                    "ai_analysis": response
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
        
        # AI API로 명령 파싱
        response = await ai_service.generate_response(command_prompt, session)
        
        if response:
            try:
                # JSON 파싱 시도
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
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
                    "ai_response": response
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
                    "ai_response": response
                }
        else:
            return {
                "original_command": command,
                "error": "명령을 파싱할 수 없습니다."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"명령 처리 오류: {str(e)}") 

@router.post("/execute-crud", summary="CRUD 명령 실행")
async def execute_crud_command(
    command: dict,
    session: Session = Depends(get_session)
):
    """CRUD 명령 실행"""
    try:
        print(f"[CRUD] 명령 수신: {command}")
        
        # 명령 분석 및 실행
        if command.get("command_type") == "student":
            if command["action"] == "create":
                new_student = Student(
                    name=command["parameters"]["name"], 
                    grade=command["parameters"]["grade"], 
                    email=command["parameters"]["email"]
                )
                session.add(new_student)
                session.commit()
                return {"success": True, "message": f"학생 '{command['parameters']['name']}' 생성됨"}
            elif command["action"] == "update":
                student = session.get(Student, command["parameters"]["id"])
                if student:
                    for key, value in command["parameters"].items():
                        if key != "id" and hasattr(student, key):
                            setattr(student, key, value)
                    session.commit()
                    return {"success": True, "message": f"학생 '{student.name}' 정보 수정됨"}
                else:
                    return {"success": False, "message": "학생을 찾을 수 없습니다"}
            elif command["action"] == "delete":
                student = session.get(Student, command["parameters"]["id"])
                if student:
                    session.delete(student)
                    session.commit()
                    return {"success": True, "message": f"학생 '{student.name}' 삭제됨"}
                else:
                    return {"success": False, "message": "학생을 찾을 수 없습니다"}
            elif command["action"] == "get":
                students = session.exec(select(Student)).all()
                return {"success": True, "students": [{"id": s.id, "name": s.name, "grade": s.grade} for s in students]}
            else:
                return {"success": False, "message": f"지원되지 않는 학생 명령: {command['action']}"}
                
        elif command.get("command_type") == "teacher":
            if command["action"] == "create":
                new_teacher = Teacher(
                    name=command["parameters"]["name"], 
                    subject=command["parameters"]["subject"], 
                    email=command["parameters"]["email"]
                )
                session.add(new_teacher)
                session.commit()
                return {"success": True, "message": f"강사 '{command['parameters']['name']}' 생성됨"}
            elif command["action"] == "update":
                teacher = session.get(Teacher, command["parameters"]["id"])
                if teacher:
                    for key, value in command["parameters"].items():
                        if key != "id" and hasattr(teacher, key):
                            setattr(teacher, key, value)
                    session.commit()
                    return {"success": True, "message": f"강사 '{teacher.name}' 정보 수정됨"}
                else:
                    return {"success": False, "message": "강사를 찾을 수 없습니다"}
            elif command["action"] == "delete":
                teacher = session.get(Teacher, command["parameters"]["id"])
                if teacher:
                    session.delete(teacher)
                    session.commit()
                    return {"success": True, "message": f"강사 '{teacher.name}' 삭제됨"}
                else:
                    return {"success": False, "message": "강사를 찾을 수 없습니다"}
            elif command["action"] == "get":
                teachers = session.exec(select(Teacher)).all()
                return {"success": True, "teachers": [{"id": t.id, "name": t.name, "subject": t.subject} for t in teachers]}
            else:
                return {"success": False, "message": f"지원되지 않는 강사 명령: {command['action']}"}
                
        elif command.get("command_type") == "material":
            if command["action"] == "create":
                new_material = Material(
                    name=command["parameters"]["name"], 
                    subject=command["parameters"]["subject"], 
                    grade=command["parameters"]["grade"]
                )
                session.add(new_material)
                session.commit()
                return {"success": True, "message": f"교재 '{command['parameters']['name']}' 생성됨"}
            elif command["action"] == "update":
                material = session.get(Material, command["parameters"]["id"])
                if material:
                    for key, value in command["parameters"].items():
                        if key != "id" and hasattr(material, key):
                            setattr(material, key, value)
                    session.commit()
                    return {"success": True, "message": f"교재 '{material.name}' 정보 수정됨"}
                else:
                    return {"success": False, "message": "교재를 찾을 수 없습니다"}
            elif command["action"] == "delete":
                material = session.get(Material, command["parameters"]["id"])
                if material:
                    session.delete(material)
                    session.commit()
                    return {"success": True, "message": f"교재 '{material.name}' 삭제됨"}
                else:
                    return {"success": False, "message": "교재를 찾을 수 없습니다"}
            elif command["action"] == "get":
                materials = session.exec(select(Material)).all()
                return {"success": True, "materials": [{"id": m.id, "name": m.name, "subject": m.subject} for m in materials]}
            else:
                return {"success": False, "message": f"지원되지 않는 교재 명령: {command['action']}"}
                
        elif command.get("command_type") == "lecture":
            if command["action"] == "create":
                new_lecture = Lecture(
                    name=command["parameters"]["name"], 
                    subject=command["parameters"]["subject"], 
                    teacher_id=command["parameters"]["teacher_id"]
                )
                session.add(new_lecture)
                session.commit()
                return {"success": True, "message": f"강의 '{command['parameters']['name']}' 생성됨"}
            elif command["action"] == "update":
                lecture = session.get(Lecture, command["parameters"]["id"])
                if lecture:
                    for key, value in command["parameters"].items():
                        if key != "id" and hasattr(lecture, key):
                            setattr(lecture, key, value)
                    session.commit()
                    return {"success": True, "message": f"강의 '{lecture.name}' 정보 수정됨"}
                else:
                    return {"success": False, "message": "강의를 찾을 수 없습니다"}
            elif command["action"] == "delete":
                lecture = session.get(Lecture, command["parameters"]["id"])
                if lecture:
                    session.delete(lecture)
                    session.commit()
                    return {"success": True, "message": f"강의 '{lecture.name}' 삭제됨"}
                else:
                    return {"success": False, "message": "강의를 찾을 수 없습니다"}
            elif command["action"] == "get":
                lectures = session.exec(select(Lecture)).all()
                return {"success": True, "lectures": [{"id": l.id, "name": l.name, "subject": l.subject} for l in lectures]}
            else:
                return {"success": False, "message": f"지원되지 않는 강의 명령: {command['action']}"}
                
        elif command.get("command_type") == "tuition":
            if command["action"] == "get":
                # 미납 학생 목록 조회 (임시 로직)
                students = session.exec(select(Student).where(Student.is_active == True, Student.tuition_fee > 0)).all()
                return {"success": True, "unpaid_students": [{"id": s.id, "name": s.name, "tuition_fee": s.tuition_fee} for s in students]}
            else:
                return {"success": False, "message": f"지원되지 않는 수강료 명령: {command['action']}"}
        else:
            return {"success": False, "message": f"지원되지 않는 명령 유형: {command['command_type']}"}
            
    except Exception as e:
        print(f"[CRUD] 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"CRUD 명령 처리 오류: {str(e)}") 

@router.get("/prompt/info", summary="현재 지침 정보 조회")
async def get_prompt_info():
    """현재 사용 중인 지침 정보 조회"""
    try:
        prompt_info = ai_service.get_current_prompt_info()
        available_prompts = PromptFactory.get_available_prompts()
        
        return {
            "current_prompt": prompt_info,
            "available_prompts": available_prompts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지침 정보 조회 오류: {str(e)}")

@router.post("/prompt/switch", summary="지침 타입 전환")
async def switch_prompt_type(prompt_type: str = Body(...)):
    """지침 타입 전환"""
    try:
        if prompt_type not in ["original", "optimized"]:
            raise HTTPException(status_code=400, detail="지원하지 않는 지침 타입입니다")
        
        ai_service.switch_prompt_type(prompt_type)
        
        return {
            "success": True,
            "message": f"지침이 {prompt_type}로 전환되었습니다",
            "current_prompt": ai_service.get_current_prompt_info()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지침 전환 오류: {str(e)}")

@router.get("/prompt/compare", summary="지침 비교 리포트")
async def get_prompt_comparison():
    """지침 비교 리포트 조회"""
    try:
        comparison = ai_service.get_prompt_comparison()
        return {
            "comparison": comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"지침 비교 리포트 조회 오류: {str(e)}") 
from typing import Dict, Any, Optional
from sqlmodel import Session
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.material import Material
from app.models.lecture import Lecture
import httpx
import asyncio
import json
import os
from datetime import datetime

class ContextBuilder:
    """컨텍스트 데이터 빌더"""
    
    @staticmethod
    async def build_context(session: Optional[Session] = None) -> Dict[str, Any]:
        """컨텍스트 데이터 구축 (단순하게 DB에서 직접 읽기)"""
        context_data = {}
        
        try:
            # 1순위: API를 통해 데이터 가져오기 (대시보드와 동일한 소스)
            api_data = await ContextBuilder._build_context_from_api(session)
            if api_data:
                print("[ContextBuilder] API에서 데이터 조회 성공")
                return api_data
            
            # 2순위: 직접 DB 조회 (fallback)
            if session:
                print("[ContextBuilder] API 실패, 직접 DB 조회")
                return await ContextBuilder._build_context_from_db(session)
            
            print("[ContextBuilder] 데이터 조회 실패")
            return {}
            
        except Exception as e:
            print(f"[ContextBuilder] 데이터 조회 오류: {e}")
            return {}
    
    @staticmethod
    async def _build_context_from_api(session: Optional[Session] = None) -> Dict[str, Any]:
        """API를 통한 컨텍스트 데이터 구축"""
        context_data = {}
        
        try:
            # 환경에 따른 API URL 설정
            if os.getenv("ENVIRONMENT") == "production" or os.getenv("RENDER"):
                # 배포 환경 (Render)
                base_url = "https://academy-ai-assistant-backend.onrender.com/api/v1"
            else:
                # 로컬 개발 환경
                base_url = "http://localhost:8000/api/v1"
            
            print(f"[ContextBuilder] API URL: {base_url}")
            
            # API를 통해 데이터 가져오기 (대시보드와 동일한 소스)
            async with httpx.AsyncClient() as client:
                # 학생 정보
                students_response = await client.get(f"{base_url}/students/")
                if students_response.status_code == 200:
                    students_data = students_response.json()
                    students = students_data.get('students', []) if isinstance(students_data, dict) else students_data
                    context_data['students'] = [
                        {
                            'name': s.get('name', ''),
                            'grade': s.get('grade', ''),
                            'email': s.get('email', ''),
                            'phone': s.get('phone', ''),
                            'tuition_fee': s.get('tuition_fee', 0),
                            'is_active': s.get('is_active', True)
                        } for s in students
                    ]
                    print(f"[ContextBuilder] API에서 학생 {len(context_data['students'])}명 조회")
                else:
                    print(f"[ContextBuilder] 학생 API 오류: {students_response.status_code}")
                
                # 강사 정보
                teachers_response = await client.get(f"{base_url}/teachers/")
                if teachers_response.status_code == 200:
                    teachers_data = teachers_response.json()
                    teachers = teachers_data.get('teachers', []) if isinstance(teachers_data, dict) else teachers_data
                    context_data['teachers'] = [
                        {
                            'name': t.get('name', ''),
                            'subject': t.get('subject', ''),
                            'email': t.get('email', ''),
                            'phone': t.get('phone', ''),
                            'hourly_rate': t.get('hourly_rate', 0),
                            'is_active': t.get('is_active', True)
                        } for t in teachers
                    ]
                    print(f"[ContextBuilder] API에서 강사 {len(context_data['teachers'])}명 조회")
                else:
                    print(f"[ContextBuilder] 강사 API 오류: {teachers_response.status_code}")
                
                # 교재 정보
                materials_response = await client.get(f"{base_url}/materials/")
                if materials_response.status_code == 200:
                    materials_data = materials_response.json()
                    materials = materials_data.get('materials', []) if isinstance(materials_data, dict) else materials_data
                    context_data['materials'] = [
                        {
                            'name': m.get('name', ''),
                            'subject': m.get('subject', ''),
                            'grade': m.get('grade', ''),
                            'publisher': m.get('publisher', ''),
                            'quantity': m.get('quantity', 0),
                            'price': m.get('price', 0),
                            'is_active': m.get('is_active', True)
                        } for m in materials
                    ]
                    print(f"[ContextBuilder] API에서 교재 {len(context_data['materials'])}개 조회")
                else:
                    print(f"[ContextBuilder] 교재 API 오류: {materials_response.status_code}")
                
                # 강의 정보
                lectures_response = await client.get(f"{base_url}/lectures/")
                if lectures_response.status_code == 200:
                    lectures_data = lectures_response.json()
                    lectures = lectures_data.get('lectures', []) if isinstance(lectures_data, dict) else lectures_data
                    context_data['lectures'] = [
                        {
                            'title': l.get('title', ''),
                            'subject': l.get('subject', ''),
                            'grade': l.get('grade', ''),
                            'schedule': l.get('schedule', ''),
                            'classroom': l.get('classroom', ''),
                            'max_students': l.get('max_students', 0),
                            'current_students': l.get('current_students', 0),
                            'tuition_fee': l.get('tuition_fee', 0),
                            'is_active': l.get('is_active', True)
                        } for l in lectures
                    ]
                    print(f"[ContextBuilder] API에서 강의 {len(context_data['lectures'])}개 조회")
                else:
                    print(f"[ContextBuilder] 강의 API 오류: {lectures_response.status_code}")
                
        except Exception as e:
            print(f"[ContextBuilder] API 조회 오류: {e}")
            return {}
        
        return context_data
    
    @staticmethod
    async def _build_context_from_db(session: Session) -> Dict[str, Any]:
        """직접 DB 조회를 통한 컨텍스트 데이터 구축"""
        context_data = {}
        
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
            
            print(f"[ContextBuilder] DB에서 직접 조회: 학생 {len(context_data['students'])}명, 강사 {len(context_data['teachers'])}명, 교재 {len(context_data['materials'])}개, 강의 {len(context_data['lectures'])}개")
            
        except Exception as e:
            print(f"[ContextBuilder] DB 조회 오류: {e}")
            context_data = {}
        
        return context_data
    
    @staticmethod
    def filter_context_by_keywords(context_data: Dict[str, Any], message: str) -> Dict[str, Any]:
        """키워드에 따른 컨텍스트 필터링"""
        message_lower = message.lower()
        filtered_context = {}
        
        # 기본 시스템 현황 (항상 포함)
        student_count = len(context_data.get('students', []))
        teacher_count = len(context_data.get('teachers', []))
        material_count = len(context_data.get('materials', []))
        lecture_count = len(context_data.get('lectures', []))
        
        filtered_context['system_summary'] = {
            'students': student_count,
            'teachers': teacher_count,
            'materials': material_count,
            'lectures': lecture_count
        }
        
        # 키워드 기반 필터링 (전체 데이터 포함)
        if any(keyword in message_lower for keyword in ['학생', 'student', '학생 목록', '학생들']):
            filtered_context['students'] = context_data.get('students', [])
            print(f"[ContextBuilder] 학생 전체 데이터 포함: {len(filtered_context['students'])}명")
            # 학생 목록 요청 시 강제로 모든 학생 포함
            if '목록' in message_lower or '전체' in message_lower or '전부' in message_lower or '모든' in message_lower:
                print(f"[ContextBuilder] 학생 목록 요청 감지 - 모든 {len(filtered_context['students'])}명 학생 포함")
                # 개수 확인 로그 추가
                actual_count = len(filtered_context['students'])
                print(f"[ContextBuilder] 실제 학생 개수: {actual_count}명")
                if actual_count != student_count:
                    print(f"[ContextBuilder] ⚠️ 경고: 시스템 요약({student_count}명)과 실제 데이터({actual_count}명) 불일치!")
        
        if any(keyword in message_lower for keyword in ['강사', 'teacher', '강사 목록', '강사들']):
            filtered_context['teachers'] = context_data.get('teachers', [])
            print(f"[ContextBuilder] 강사 전체 데이터 포함: {len(filtered_context['teachers'])}명")
            # 강사 목록 요청 시 강제로 모든 강사 포함
            if '목록' in message_lower or '전체' in message_lower or '전부' in message_lower or '모든' in message_lower:
                print(f"[ContextBuilder] 강사 목록 요청 감지 - 모든 {len(filtered_context['teachers'])}명 강사 포함")
        
        if any(keyword in message_lower for keyword in ['교재', 'material', '교재 목록', '교재들']):
            filtered_context['materials'] = context_data.get('materials', [])
            print(f"[ContextBuilder] 교재 전체 데이터 포함: {len(filtered_context['materials'])}개")
            # 교재 목록 요청 시 강제로 모든 교재 포함
            if '목록' in message_lower or '전체' in message_lower or '전부' in message_lower or '모든' in message_lower:
                print(f"[ContextBuilder] 교재 목록 요청 감지 - 모든 {len(filtered_context['materials'])}개 교재 포함")
        
        if any(keyword in message_lower for keyword in ['강의', 'lecture', '강의 목록', '강의들']):
            filtered_context['lectures'] = context_data.get('lectures', [])
            print(f"[ContextBuilder] 강의 전체 데이터 포함: {len(filtered_context['lectures'])}개")
            # 강의 목록 요청 시 강제로 모든 강의 포함
            if '목록' in message_lower or '전체' in message_lower or '전부' in message_lower or '모든' in message_lower:
                print(f"[ContextBuilder] 강의 목록 요청 감지 - 모든 {len(filtered_context['lectures'])}개 강의 포함")
                # 개수 확인 로그 추가
                actual_count = len(filtered_context['lectures'])
                print(f"[ContextBuilder] 실제 강의 개수: {actual_count}개")
                if actual_count != lecture_count:
                    print(f"[ContextBuilder] ⚠️ 경고: 시스템 요약({lecture_count}개)과 실제 데이터({actual_count}개) 불일치!")
        
        # 전체 요청인 경우 모든 데이터 포함 (키워드 확장)
        if any(keyword in message_lower for keyword in ['전체', '모든', 'all', '전체 목록', '모든 목록', '전부', '다', '모두']):
            filtered_context.update(context_data)
            print(f"[ContextBuilder] 전체 요청 감지 - 모든 데이터 포함")
        
        # 기본 데이터 포함 (최근 5개씩) - 목록 요청이 아닐 때만
        if not any(keyword in message_lower for keyword in ['목록', '전체', '전부', '모든', 'all']):
            filtered_context['recent_students'] = context_data.get('students', [])[:5]
            filtered_context['recent_teachers'] = context_data.get('teachers', [])[:5]
            filtered_context['recent_materials'] = context_data.get('materials', [])[:5]
            filtered_context['recent_lectures'] = context_data.get('lectures', [])[:5]
        
        return filtered_context 
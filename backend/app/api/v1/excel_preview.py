from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict, Any, List
import json
import os
from datetime import datetime
from app.core.database import get_session
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.material import Material
from app.models.lecture import Lecture

router = APIRouter()

# 엑셀 미리보기 데이터 저장 디렉토리
EXCEL_PREVIEW_DIR = "excel_preview_data"
os.makedirs(EXCEL_PREVIEW_DIR, exist_ok=True)

def save_excel_preview_data(entity_type: str, data: List[Dict[str, Any]]):
    """엑셀 미리보기 데이터를 파일로 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{entity_type}_{timestamp}.json"
    filepath = os.path.join(EXCEL_PREVIEW_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    return filepath

def get_latest_excel_preview_data(entity_type: str) -> List[Dict[str, Any]]:
    """최신 엑셀 미리보기 데이터를 파일에서 읽기"""
    try:
        files = [f for f in os.listdir(EXCEL_PREVIEW_DIR) if f.startswith(f"{entity_type}_")]
        if not files:
            return []
        
        # 가장 최신 파일 찾기
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(EXCEL_PREVIEW_DIR, x)))
        filepath = os.path.join(EXCEL_PREVIEW_DIR, latest_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"엑셀 미리보기 데이터 읽기 실패: {e}")
        return []

@router.post("/generate/{entity_type}", summary="엑셀 미리보기 데이터 생성")
async def generate_excel_preview(
    entity_type: str,
    session: Session = Depends(get_session)
):
    """DB 데이터를 엑셀 미리보기 형식으로 변환하여 저장"""
    try:
        if entity_type == "students":
            # 학생 데이터 조회 및 변환
            students = session.query(Student).all()
            students = sorted(students, key=lambda x: x.created_at, reverse=True)
            
            excel_data = []
            for student in students:
                excel_data.append({
                    "이름": student.name,
                    "학년": student.grade,
                    "이메일": student.email,
                    "전화번호": student.phone,
                    "수강료": student.tuition_fee,
                    "활성화 여부": "활성" if student.is_active else "비활성",
                    "등록일": student.created_at.strftime("%Y-%m-%d") if student.created_at else ""
                })
            
            filepath = save_excel_preview_data("students", excel_data)
            return {"message": "학생 엑셀 미리보기 데이터 생성 완료", "filepath": filepath, "count": len(excel_data)}
            
        elif entity_type == "teachers":
            # 강사 데이터 조회 및 변환
            teachers = session.query(Teacher).all()
            teachers = sorted(teachers, key=lambda x: x.created_at, reverse=True)
            
            excel_data = []
            for teacher in teachers:
                excel_data.append({
                    "이름": teacher.name,
                    "과목": teacher.subject,
                    "이메일": teacher.email,
                    "전화번호": teacher.phone,
                    "시간당 급여": teacher.hourly_rate,
                    "활성화 여부": "활성" if teacher.is_active else "비활성",
                    "등록일": teacher.created_at.strftime("%Y-%m-%d") if teacher.created_at else ""
                })
            
            filepath = save_excel_preview_data("teachers", excel_data)
            return {"message": "강사 엑셀 미리보기 데이터 생성 완료", "filepath": filepath, "count": len(excel_data)}
            
        elif entity_type == "materials":
            # 교재 데이터 조회 및 변환
            materials = session.query(Material).all()
            materials = sorted(materials, key=lambda x: x.created_at, reverse=True)
            
            excel_data = []
            for material in materials:
                excel_data.append({
                    "과목": material.subject,
                    "학년": material.grade,
                    "이름": material.name,
                    "출판사": material.publisher,
                    "수량": material.quantity,
                    "가격": material.price,
                    "활성화 여부": "활성" if material.is_active else "비활성",
                    "등록일": material.created_at.strftime("%Y-%m-%d") if material.created_at else ""
                })
            
            filepath = save_excel_preview_data("materials", excel_data)
            return {"message": "교재 엑셀 미리보기 데이터 생성 완료", "filepath": filepath, "count": len(excel_data)}
            
        elif entity_type == "lectures":
            # 강의 데이터 조회 및 변환
            lectures = session.query(Lecture).all()
            lectures = sorted(lectures, key=lambda x: x.created_at, reverse=True)
            
            excel_data = []
            for lecture in lectures:
                excel_data.append({
                    "강의 제목": lecture.title,
                    "과목": lecture.subject,
                    "학년": lecture.grade,
                    "일정": lecture.schedule,
                    "강의실": lecture.classroom,
                    "수강생 수": f"{lecture.current_students}/{lecture.max_students}",
                    "수강료": lecture.tuition_fee,
                    "활성화 여부": "활성" if lecture.is_active else "비활성",
                    "등록일": lecture.created_at.strftime("%Y-%m-%d") if lecture.created_at else ""
                })
            
            filepath = save_excel_preview_data("lectures", excel_data)
            return {"message": "강의 엑셀 미리보기 데이터 생성 완료", "filepath": filepath, "count": len(excel_data)}
            
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 엔티티 타입입니다")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"엑셀 미리보기 데이터 생성 실패: {str(e)}")

@router.get("/data/{entity_type}", summary="엑셀 미리보기 데이터 조회")
async def get_excel_preview_data(entity_type: str):
    """엑셀 미리보기 데이터 조회"""
    try:
        data = get_latest_excel_preview_data(entity_type)
        return {
            "entity_type": entity_type,
            "data": data,
            "count": len(data),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"엑셀 미리보기 데이터 조회 실패: {str(e)}")

@router.post("/generate/all", summary="모든 엔티티 엑셀 미리보기 데이터 생성")
async def generate_all_excel_preview(session: Session = Depends(get_session)):
    """모든 엔티티의 엑셀 미리보기 데이터를 한 번에 생성"""
    try:
        results = {}
        
        for entity_type in ["students", "teachers", "materials", "lectures"]:
            response = await generate_excel_preview(entity_type, session)
            results[entity_type] = response
            
        return {
            "message": "모든 엔티티 엑셀 미리보기 데이터 생성 완료",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전체 엑셀 미리보기 데이터 생성 실패: {str(e)}") 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from app.models import Teacher, TeacherCreate, TeacherUpdate
from app.core.database import get_session
from app.core.auth import AuthService
from app.services.teacher_service import TeacherService
import json
from datetime import datetime

router = APIRouter()

@router.get("/", summary="강사 목록 조회")
def get_teachers(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """강사 목록을 조회합니다."""
    statement = select(Teacher).offset(skip).limit(limit)
    teachers = session.exec(statement).all()
    return {"teachers": teachers}

@router.get("/{teacher_id}", response_model=Teacher, summary="강사 상세 조회")
def get_teacher(
    teacher_id: int,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """특정 강사의 상세 정보를 조회합니다."""
    statement = select(Teacher).where(Teacher.id == teacher_id)
    teacher = session.exec(statement).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.post("/", response_model=Teacher, summary="강사 등록")
def create_teacher(
    teacher: TeacherCreate,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """새로운 강사를 등록합니다."""
    # certification 필드를 JSON 문자열로 변환
    teacher_data = teacher.dict()
    if isinstance(teacher_data.get('certification'), list):
        teacher_data['certification'] = json.dumps(teacher_data['certification'])
    
    # hire_date가 None인 경우 현재 시간으로 설정
    if teacher_data.get('hire_date') is None:
        teacher_data['hire_date'] = datetime.utcnow()
    
    db_teacher = Teacher(**teacher_data)
    session.add(db_teacher)
    session.commit()
    session.refresh(db_teacher)
    return db_teacher

@router.put("/{teacher_id}", response_model=Teacher, summary="강사 정보 수정")
def update_teacher(
    teacher_id: int,
    teacher: TeacherUpdate,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """강사 정보를 수정합니다."""
    statement = select(Teacher).where(Teacher.id == teacher_id)
    db_teacher = session.exec(statement).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    teacher_data = teacher.dict(exclude_unset=True)
    
    # certification 필드를 JSON 문자열로 변환
    if 'certification' in teacher_data and isinstance(teacher_data['certification'], list):
        teacher_data['certification'] = json.dumps(teacher_data['certification'])
    
    for key, value in teacher_data.items():
        setattr(db_teacher, key, value)
    
    session.add(db_teacher)
    session.commit()
    session.refresh(db_teacher)
    return db_teacher

@router.delete("/{teacher_id}", summary="강사 삭제")
def delete_teacher(
    teacher_id: int,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """강사를 삭제합니다 (소프트 삭제)."""
    service = TeacherService(session)
    success = service.delete_teacher(teacher_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    return {"message": "Teacher deleted successfully"}


@router.delete("/{teacher_id}/hard", summary="강사 완전 삭제")
def hard_delete_teacher(
    teacher_id: int,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """강사를 완전히 삭제합니다 (하드 딜리트)."""
    service = TeacherService(session)
    success = service.hard_delete_teacher(teacher_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    return {"message": f"Teacher {teacher_id} permanently deleted"} 
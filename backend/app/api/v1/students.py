from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Optional

from ...core.database import get_session
from ...schemas.student import (
    StudentCreate, 
    StudentUpdate, 
    StudentResponse, 
    StudentListResponse
)
from ...services.student_service import StudentService

router = APIRouter()


@router.get("/", response_model=StudentListResponse)
def get_students(
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_session)
):
    """학생 목록 조회"""
    service = StudentService(db)
    students = service.get_students(skip=skip, limit=limit, is_active=is_active)
    total = service.count_students(is_active=is_active)
    
    return StudentListResponse(
        students=[StudentResponse.from_orm(s) for s in students],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_session)):
    """학생 상세 조회"""
    service = StudentService(db)
    student = service.get_student(student_id)
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(student_data: StudentCreate, db: Session = Depends(get_session)):
    """학생 등록"""
    print(f"받은 학생 데이터: {student_data}")
    service = StudentService(db)
    
    # 이메일 중복 확인
    existing_student = service.get_student_by_email(student_data.email)
    if existing_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    student = service.create_student(student_data)
    print(f"생성된 학생: {student}")
    return student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int, 
    student_data: StudentUpdate, 
    db: Session = Depends(get_session)
):
    """학생 정보 수정"""
    service = StudentService(db)
    
    # 이메일 변경 시 중복 확인
    if student_data.email:
        existing_student = service.get_student_by_email(student_data.email)
        if existing_student and existing_student.id != student_id:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    student = service.update_student(student_id, student_data)
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_session)):
    """학생 삭제 (소프트 삭제)"""
    service = StudentService(db)
    success = service.delete_student(student_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Student not found") 


@router.delete("/{student_id}/hard", status_code=204)
def hard_delete_student(student_id: int, db: Session = Depends(get_session)):
    """학생 완전 삭제 (하드 딜리트)"""
    service = StudentService(db)
    success = service.hard_delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found") 
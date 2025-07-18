from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import Optional

from ...core.database import get_session
from ...models.lecture import LectureCreate, LectureUpdate
from ...schemas.lecture import LectureResponse, LectureListResponse
from ...services.lecture_service import LectureService

router = APIRouter()

@router.get("/", response_model=LectureListResponse)
def get_lectures(
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_session)
):
    """강의 목록 조회"""
    service = LectureService(db)
    lectures = service.get_lectures(skip=skip, limit=limit, is_active=is_active)
    total = service.count_lectures(is_active=is_active)
    
    return LectureListResponse(
        lectures=[LectureResponse.from_orm(l) for l in lectures],
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{lecture_id}", response_model=LectureResponse)
def get_lecture(lecture_id: int, db: Session = Depends(get_session)):
    """강의 상세 조회"""
    service = LectureService(db)
    lecture = service.get_lecture(lecture_id)
    
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    return LectureResponse.from_orm(lecture)

@router.post("/", response_model=LectureResponse, status_code=201)
def create_lecture(lecture_data: LectureCreate, db: Session = Depends(get_session)):
    """강의 등록"""
    service = LectureService(db)
    lecture = service.create_lecture(lecture_data)
    return LectureResponse.from_orm(lecture)

@router.put("/{lecture_id}", response_model=LectureResponse)
def update_lecture(lecture_id: int, lecture_data: LectureUpdate, db: Session = Depends(get_session)):
    """강의 정보 수정"""
    service = LectureService(db)
    lecture = service.update_lecture(lecture_id, lecture_data)
    
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    return LectureResponse.from_orm(lecture)

@router.delete("/{lecture_id}")
def delete_lecture(lecture_id: int, db: Session = Depends(get_session)):
    """강의 삭제"""
    service = LectureService(db)
    success = service.delete_lecture(lecture_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Lecture not found")
    
    return {"message": "Lecture deleted successfully"} 
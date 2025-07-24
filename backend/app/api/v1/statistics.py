from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Dict
from app.core.database import get_session
from app.services.statistics_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/students")
async def get_student_statistics(db: Session = Depends(get_session)) -> Dict:
    """학생 관련 기본 통계 조회"""
    try:
        stats_service = StatisticsService(db)
        return stats_service.get_student_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"학생 통계 조회 실패: {str(e)}")


@router.get("/lectures")
async def get_lecture_statistics(db: Session = Depends(get_session)) -> Dict:
    """강의 관련 기본 통계 조회"""
    try:
        stats_service = StatisticsService(db)
        return stats_service.get_lecture_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"강의 통계 조회 실패: {str(e)}")


@router.get("/teachers")
async def get_teacher_statistics(db: Session = Depends(get_session)) -> Dict:
    """강사 관련 기본 통계 조회"""
    try:
        stats_service = StatisticsService(db)
        return stats_service.get_teacher_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"강사 통계 조회 실패: {str(e)}")


@router.get("/materials")
async def get_material_statistics(db: Session = Depends(get_session)) -> Dict:
    """교재 관련 기본 통계 조회"""
    try:
        stats_service = StatisticsService(db)
        return stats_service.get_material_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"교재 통계 조회 실패: {str(e)}")


@router.get("/overall")
async def get_overall_statistics(db: Session = Depends(get_session)) -> Dict:
    """전체 종합 통계 조회"""
    try:
        stats_service = StatisticsService(db)
        return stats_service.get_overall_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전체 통계 조회 실패: {str(e)}") 
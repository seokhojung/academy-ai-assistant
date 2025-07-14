from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session
from typing import Dict, Any
from app.core.database import get_session
from app.core.auth import AuthService
from app.workers.excel_rebuilder import (
    rebuild_student_excel,
    rebuild_teacher_excel,
    rebuild_material_excel
)

router = APIRouter()

@router.post("/rebuild/students", summary="학생 Excel 파일 재생성")
async def trigger_student_excel_rebuild(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user = Depends(AuthService.get_current_active_user)
):
    """학생 데이터로 Excel 파일을 재생성합니다."""
    try:
        # Celery 태스크 실행
        task = rebuild_student_excel.delay()
        
        return {
            "message": "학생 Excel 파일 재생성이 시작되었습니다.",
            "task_id": task.id,
            "status": "PENDING"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel 재생성 오류: {str(e)}")

@router.post("/rebuild/teachers", summary="강사 Excel 파일 재생성")
async def trigger_teacher_excel_rebuild(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user = Depends(AuthService.get_current_active_user)
):
    """강사 데이터로 Excel 파일을 재생성합니다."""
    try:
        # Celery 태스크 실행
        task = rebuild_teacher_excel.delay()
        
        return {
            "message": "강사 Excel 파일 재생성이 시작되었습니다.",
            "task_id": task.id,
            "status": "PENDING"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel 재생성 오류: {str(e)}")

@router.post("/rebuild/materials", summary="교재 Excel 파일 재생성")
async def trigger_material_excel_rebuild(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user = Depends(AuthService.get_current_active_user)
):
    """교재 데이터로 Excel 파일을 재생성합니다."""
    try:
        # Celery 태스크 실행
        task = rebuild_material_excel.delay()
        
        return {
            "message": "교재 Excel 파일 재생성이 시작되었습니다.",
            "task_id": task.id,
            "status": "PENDING"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel 재생성 오류: {str(e)}")

@router.get("/status/{task_id}", summary="Excel 재생성 상태 확인")
async def get_excel_rebuild_status(
    task_id: str,
    session: Session = Depends(get_session),
    current_user = Depends(AuthService.get_current_active_user)
):
    """Excel 재생성 태스크의 상태를 확인합니다."""
    try:
        from celery.result import AsyncResult
        from app.workers.celery_app import celery_app
        
        # Celery 태스크 결과 조회
        result = AsyncResult(task_id, app=celery_app)
        
        if result.ready():
            if result.successful():
                return {
                    "task_id": task_id,
                    "status": "SUCCESS",
                    "result": result.result
                }
            else:
                return {
                    "task_id": task_id,
                    "status": "FAILURE",
                    "error": str(result.result)
                }
        else:
            return {
                "task_id": task_id,
                "status": result.state,
                "info": result.info
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 확인 오류: {str(e)}")

@router.post("/rebuild/all", summary="전체 Excel 파일 재생성")
async def trigger_all_excel_rebuild(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user = Depends(AuthService.get_current_active_user)
):
    """모든 데이터로 Excel 파일을 재생성합니다."""
    try:
        # 모든 Celery 태스크 실행
        student_task = rebuild_student_excel.delay()
        teacher_task = rebuild_teacher_excel.delay()
        material_task = rebuild_material_excel.delay()
        
        return {
            "message": "전체 Excel 파일 재생성이 시작되었습니다.",
            "tasks": {
                "students": {
                    "task_id": student_task.id,
                    "status": "PENDING"
                },
                "teachers": {
                    "task_id": teacher_task.id,
                    "status": "PENDING"
                },
                "materials": {
                    "task_id": material_task.id,
                    "status": "PENDING"
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel 재생성 오류: {str(e)}") 
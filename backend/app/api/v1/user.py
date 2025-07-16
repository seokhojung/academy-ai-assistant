from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from typing import List
from ...core.database import get_session
from ...services.user_service import (
    get_user_by_firebase_uid,
    get_or_create_user_column_settings,
    update_user_column_settings,
    get_column_settings_dict
)
from ...schemas.user import UserColumnSettingsUpdate
from ...models.user import User
# from ...core.auth import get_current_user

router = APIRouter()


@router.get("/column-settings/{page_name}")
def get_column_settings(
    page_name: str,
    # current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """사용자별 컬럼 설정 가져오기"""
    try:
        # 임시로 테스트용 사용자 생성 (로컬 개발용)
        test_user = get_user_by_firebase_uid(db, "test_user")
        if not test_user:
            # 테스트용 사용자 생성
            test_user = User(
                firebase_uid="test_user",
                email="test@example.com",
                name="Test User",
                role="admin"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        
        user = test_user
        
        # 기본 컬럼 설정 (페이지별로 다름)
        default_columns = {
            "students": ["name", "email", "phone", "grade", "class_name", "tuition_fee", "tuition_due_date"],
            "teachers": ["name", "email", "phone", "subject", "hire_date"],
            "materials": ["title", "subject", "grade", "file_url", "created_at"]
        }
        
        # 사용자 설정 가져오기 (없으면 기본값으로 생성)
        if user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        settings = get_or_create_user_column_settings(
            db, user.id, page_name, default_columns.get(page_name, [])
        )
        
        return get_column_settings_dict(settings)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/column-settings/{page_name}")
def update_column_settings(
    page_name: str,
    settings: UserColumnSettingsUpdate = Body(...),
    # current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """사용자별 컬럼 설정 업데이트"""
    try:
        # 임시로 테스트용 사용자 생성 (로컬 개발용)
        test_user = get_user_by_firebase_uid(db, "test_user")
        if not test_user:
            # 테스트용 사용자 생성
            test_user = User(
                firebase_uid="test_user",
                email="test@example.com",
                name="Test User",
                role="admin"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        
        user = test_user
        
        # 설정 업데이트
        if user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        updated_settings = update_user_column_settings(db, user.id, page_name, settings)
        if not updated_settings:
            raise HTTPException(status_code=404, detail="Column settings not found")
        
        return get_column_settings_dict(updated_settings)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
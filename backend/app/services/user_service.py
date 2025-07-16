from sqlmodel import Session, select
from typing import List, Optional
import json
from ..models.user import User, UserColumnSettings
from ..schemas.user import UserColumnSettingsCreate, UserColumnSettingsUpdate


def get_user_by_firebase_uid(db: Session, firebase_uid: str) -> Optional[User]:
    return db.exec(select(User).where(User.firebase_uid == firebase_uid)).first()


def get_user_column_settings(db: Session, user_id: int, page_name: str) -> Optional[UserColumnSettings]:
    return db.exec(
        select(UserColumnSettings)
        .where(UserColumnSettings.user_id == user_id)
        .where(UserColumnSettings.page_name == page_name)
    ).first()


def create_user_column_settings(db: Session, settings: UserColumnSettingsCreate) -> UserColumnSettings:
    db_settings = UserColumnSettings(
        user_id=settings.user_id,
        page_name=settings.page_name,
        visible_columns=json.dumps(settings.visible_columns),
        hidden_columns=json.dumps(settings.hidden_columns),
        column_order=json.dumps(settings.column_order)
    )
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings


def update_user_column_settings(db: Session, user_id: int, page_name: str, settings: UserColumnSettingsUpdate) -> Optional[UserColumnSettings]:
    db_settings = get_user_column_settings(db, user_id, page_name)
    if db_settings:
        db_settings.visible_columns = json.dumps(settings.visible_columns)
        db_settings.hidden_columns = json.dumps(settings.hidden_columns)
        db_settings.column_order = json.dumps(settings.column_order)
        db.commit()
        db.refresh(db_settings)
    return db_settings


def get_or_create_user_column_settings(db: Session, user_id: int, page_name: str, default_columns: List[str]) -> UserColumnSettings:
    settings = get_user_column_settings(db, user_id, page_name)
    if not settings:
        # 기본 설정 생성
        create_data = UserColumnSettingsCreate(
            user_id=user_id,
            page_name=page_name,
            visible_columns=default_columns,
            hidden_columns=[],
            column_order=default_columns
        )
        settings = create_user_column_settings(db, create_data)
    return settings


def get_column_settings_dict(settings: UserColumnSettings) -> dict:
    return {
        "visible_columns": json.loads(settings.visible_columns),
        "hidden_columns": json.loads(settings.hidden_columns),
        "column_order": json.loads(settings.column_order)
    } 
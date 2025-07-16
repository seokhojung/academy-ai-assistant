from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserColumnSettingsBase(BaseModel):
    page_name: str
    visible_columns: List[str]
    hidden_columns: List[str]
    column_order: List[str]


class UserColumnSettingsCreate(UserColumnSettingsBase):
    user_id: int


class UserColumnSettingsUpdate(BaseModel):
    visible_columns: List[str]
    hidden_columns: List[str]
    column_order: List[str]


class UserColumnSettings(UserColumnSettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 
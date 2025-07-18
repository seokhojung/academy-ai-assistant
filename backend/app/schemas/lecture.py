from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LectureResponse(BaseModel):
    id: int
    title: str
    subject: str
    teacher_id: Optional[int] = None
    material_id: Optional[int] = None
    grade: str
    max_students: int
    current_students: int
    tuition_fee: int
    schedule: str
    classroom: str
    is_active: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LectureListResponse(BaseModel):
    lectures: list[LectureResponse]
    total: int
    page: int
    size: int 
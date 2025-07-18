from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Lecture(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    subject: str = Field(index=True)
    teacher_id: Optional[int] = Field(default=None, foreign_key="teacher.id")
    material_id: Optional[int] = Field(default=None, foreign_key="material.id")
    grade: str = Field(index=True)
    max_students: int = Field(default=20)
    current_students: int = Field(default=0)
    tuition_fee: int = Field(default=0)
    schedule: str = Field(default="")  # "월수금 14:00-16:00" 형태
    classroom: str = Field(default="")
    is_active: bool = Field(default=True, index=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LectureCreate(SQLModel):
    title: str
    subject: str
    teacher_id: Optional[int] = None
    material_id: Optional[int] = None
    grade: str
    max_students: int = 20
    tuition_fee: int = 0
    schedule: str = ""
    classroom: str = ""
    is_active: bool = True
    description: Optional[str] = None

class LectureUpdate(SQLModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    teacher_id: Optional[int] = None
    material_id: Optional[int] = None
    grade: Optional[str] = None
    max_students: Optional[int] = None
    tuition_fee: Optional[int] = None
    schedule: Optional[str] = None
    classroom: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None 
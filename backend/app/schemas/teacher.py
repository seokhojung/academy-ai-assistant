from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TeacherBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    hourly_rate: float = 0.0


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    subject: Optional[str] = None
    hourly_rate: Optional[float] = None
    is_active: Optional[bool] = None


class TeacherResponse(TeacherBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeacherListResponse(BaseModel):
    teachers: list[TeacherResponse]
    total: int
    page: int
    size: int 
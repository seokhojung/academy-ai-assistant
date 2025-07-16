from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    grade: Optional[str] = None
    tuition_fee: float = 0.0
    tuition_due_date: Optional[datetime] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    grade: Optional[str] = None
    tuition_fee: Optional[float] = None
    tuition_due_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class StudentListResponse(BaseModel):
    students: list[StudentResponse]
    total: int
    page: int
    size: int 
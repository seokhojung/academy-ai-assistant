from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=100, unique=True)
    phone: Optional[str] = Field(max_length=20, default=None)
    grade: Optional[str] = Field(max_length=20, default=None)
    tuition_fee: float = Field(default=0.0)
    tuition_due_date: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 
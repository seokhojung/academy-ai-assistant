from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Teacher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=100, unique=True)
    phone: Optional[str] = Field(max_length=20, default=None)
    subject: str = Field(max_length=100)
    hourly_rate: float = Field(default=0.0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TeacherCreate(SQLModel):
    name: str = Field(max_length=100)
    email: str = Field(max_length=100)
    phone: Optional[str] = Field(max_length=20, default=None)
    subject: str = Field(max_length=100)
    hourly_rate: float = Field(default=0.0)
    is_active: bool = Field(default=True)


class TeacherUpdate(SQLModel):
    name: Optional[str] = Field(max_length=100, default=None)
    email: Optional[str] = Field(max_length=100, default=None)
    phone: Optional[str] = Field(max_length=20, default=None)
    subject: Optional[str] = Field(max_length=100, default=None)
    hourly_rate: Optional[float] = Field(default=None)
    is_active: Optional[bool] = Field(default=None) 
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    firebase_uid: str = Field(unique=True)
    email: str = Field(max_length=100, unique=True)
    name: str = Field(max_length=100)
    role: str = Field(max_length=20, default="user")  # admin, teacher, student
    is_active: bool = Field(default=True)
    password: str = Field(default="", max_length=128)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 
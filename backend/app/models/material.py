from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Material(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    subject: str = Field(max_length=100)
    grade: str = Field(max_length=20)
    quantity: int = Field(default=0)
    min_quantity: int = Field(default=5)
    price: float = Field(default=0.0)
    expiry_date: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MaterialCreate(SQLModel):
    name: str = Field(max_length=200)
    subject: str = Field(max_length=100)
    grade: str = Field(max_length=20)
    quantity: int = Field(default=0)
    min_quantity: int = Field(default=5)
    price: float = Field(default=0.0)
    expiry_date: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)


class MaterialUpdate(SQLModel):
    name: Optional[str] = Field(max_length=200, default=None)
    subject: Optional[str] = Field(max_length=100, default=None)
    grade: Optional[str] = Field(max_length=20, default=None)
    quantity: Optional[int] = Field(default=None)
    min_quantity: Optional[int] = Field(default=None)
    price: Optional[float] = Field(default=None)
    expiry_date: Optional[datetime] = Field(default=None)
    is_active: Optional[bool] = Field(default=None) 
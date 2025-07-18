from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MaterialBase(BaseModel):
    name: str
    subject: str
    grade: str
    description: Optional[str] = None
    price: float
    publisher: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    quantity: Optional[int] = 0
    min_quantity: Optional[int] = 5
    publication_date: Optional[datetime] = None
    edition: Optional[str] = None
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = True

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    publisher: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    quantity: Optional[int] = None
    min_quantity: Optional[int] = None
    publication_date: Optional[datetime] = None
    edition: Optional[str] = None
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class MaterialResponse(MaterialBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MaterialListResponse(BaseModel):
    materials: list[MaterialResponse]
    total: int
    page: int
    size: int 
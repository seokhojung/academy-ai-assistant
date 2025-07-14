from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MaterialBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    publisher: Optional[str] = None
    author: Optional[str] = None
    stock: Optional[int] = 0
    is_active: Optional[bool] = True

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    publisher: Optional[str] = None
    author: Optional[str] = None
    stock: Optional[int] = None
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
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime

from ..models.material import Material
from ..schemas.material import MaterialCreate, MaterialUpdate


class MaterialService:
    def __init__(self, db: Session):
        self.db = db

    def get_materials(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None
    ) -> list[Material]:
        """교재 목록 조회"""
        query = select(Material)
        
        if is_active is not None:
            query = query.where(Material.is_active == is_active)
        
        query = query.offset(skip).limit(limit)
        return list(self.db.exec(query).all())

    def get_material(self, material_id: int) -> Optional[Material]:
        """교재 상세 조회"""
        return self.db.get(Material, material_id)

    def create_material(self, material_data: MaterialCreate) -> Material:
        """교재 등록"""
        material = Material(**material_data.model_dump())
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)
        return material

    def update_material(self, material_id: int, material_data: MaterialUpdate) -> Optional[Material]:
        """교재 정보 수정"""
        material = self.db.get(Material, material_id)
        if not material:
            return None
        
        update_data = material_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(material, field, value)
        
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)
        return material

    def delete_material(self, material_id: int) -> bool:
        """교재 삭제 (소프트 삭제)"""
        material = self.db.get(Material, material_id)
        if not material:
            return False
        
        material.is_active = False
        material.updated_at = datetime.utcnow()
        
        self.db.add(material)
        self.db.commit()
        return True

    def get_material_by_isbn(self, isbn: str) -> Optional[Material]:
        """ISBN으로 교재 조회"""
        query = select(Material).where(Material.isbn == isbn)
        return self.db.exec(query).first()

    def count_materials(self, is_active: Optional[bool] = None) -> int:
        """교재 수 조회"""
        query = select(Material)
        
        if is_active is not None:
            query = query.where(Material.is_active == is_active)
        
        return len(self.db.exec(query).all()) 
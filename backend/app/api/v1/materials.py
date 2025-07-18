from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from app.models import Material, MaterialCreate, MaterialUpdate
from app.core.database import get_session
from app.core.auth import AuthService

router = APIRouter()

@router.get("/", response_model=List[Material], summary="교재 목록 조회")
def get_materials(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """교재 목록을 조회합니다."""
    statement = select(Material).offset(skip).limit(limit)
    materials = session.exec(statement).all()
    return materials

@router.get("/{material_id}", response_model=Material, summary="교재 상세 조회")
def get_material(
    material_id: int,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """특정 교재의 상세 정보를 조회합니다."""
    statement = select(Material).where(Material.id == material_id)
    material = session.exec(statement).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material

@router.post("/", response_model=Material, summary="교재 등록")
def create_material(
    material: MaterialCreate,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """새로운 교재를 등록합니다."""
    db_material = Material.from_orm(material)
    session.add(db_material)
    session.commit()
    session.refresh(db_material)
    return db_material

@router.put("/{material_id}", response_model=Material, summary="교재 정보 수정")
def update_material(
    material_id: int,
    material: MaterialUpdate,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """교재 정보를 수정합니다."""
    statement = select(Material).where(Material.id == material_id)
    db_material = session.exec(statement).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    material_data = material.dict(exclude_unset=True)
    for key, value in material_data.items():
        setattr(db_material, key, value)
    
    session.add(db_material)
    session.commit()
    session.refresh(db_material)
    return db_material

@router.delete("/{material_id}", summary="교재 삭제")
def delete_material(
    material_id: int,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """교재를 삭제합니다."""
    statement = select(Material).where(Material.id == material_id)
    material = session.exec(statement).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    session.delete(material)
    session.commit()
    return {"message": "Material deleted successfully"} 
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialResponse, MaterialListResponse
from app.core.database import get_session
from app.core.auth import AuthService
from app.services.material_service import MaterialService

router = APIRouter()

@router.get("/", response_model=MaterialListResponse, summary="교재 목록 조회")
def get_materials(
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """교재 목록을 조회합니다."""
    service = MaterialService(session)
    materials = service.get_materials(skip=skip, limit=limit, is_active=is_active)
    total = len(materials)  # MaterialService에 count_materials 메서드가 있다면 그것을 사용
    
    return MaterialListResponse(
        materials=[MaterialResponse.from_orm(m) for m in materials],
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{material_id}", response_model=MaterialResponse, summary="교재 상세 조회")
def get_material(
    material_id: int,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """특정 교재의 상세 정보를 조회합니다."""
    service = MaterialService(session)
    material = service.get_material(material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return MaterialResponse.from_orm(material)

@router.post("/", response_model=MaterialResponse, summary="교재 등록", status_code=201)
def create_material(
    material: MaterialCreate,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """새로운 교재를 등록합니다."""
    print(f"받은 교재 데이터: {material}")
    service = MaterialService(session)
    
    # ISBN 중복 확인 (ISBN이 있는 경우)
    if material.isbn:
        existing_material = service.get_material_by_isbn(material.isbn)
        if existing_material:
            raise HTTPException(status_code=400, detail="ISBN already registered")
    
    db_material = service.create_material(material)
    print(f"생성된 교재: {db_material}")
    return MaterialResponse.from_orm(db_material)

@router.put("/{material_id}", response_model=MaterialResponse, summary="교재 정보 수정")
def update_material(
    material_id: int,
    material: MaterialUpdate,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """교재 정보를 수정합니다."""
    print(f"PUT /materials/{material_id} - 받은 데이터: {material}")
    service = MaterialService(session)
    
    try:
        db_material = service.update_material(material_id, material)
        
        if not db_material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        print(f"업데이트 성공: {db_material}")
        return MaterialResponse.from_orm(db_material)
    except Exception as e:
        print(f"업데이트 실패: {e}")
        raise

@router.delete("/{material_id}", summary="교재 삭제", status_code=204)
def delete_material(
    material_id: int,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """교재를 삭제합니다 (소프트 삭제)."""
    service = MaterialService(session)
    success = service.delete_material(material_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Material not found")

@router.delete("/{material_id}/hard", summary="교재 완전 삭제")
def hard_delete_material(
    material_id: int,
    session: Session = Depends(get_session)
    # current_user = Depends(AuthService.get_current_active_user)  # 임시 비활성화
):
    """교재를 완전히 삭제합니다 (하드 딜리트)."""
    service = MaterialService(session)
    success = service.hard_delete_material(material_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Material not found")
    
    return {"message": f"Material {material_id} permanently deleted"} 
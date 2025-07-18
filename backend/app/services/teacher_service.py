from sqlmodel import Session, select, desc
from typing import Optional
from datetime import datetime

from ..models.teacher import Teacher
from ..schemas.teacher import TeacherCreate, TeacherUpdate


class TeacherService:
    def __init__(self, db: Session):
        self.db = db

    def get_teachers(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None
    ) -> list[Teacher]:
        """강사 목록 조회"""
        query = select(Teacher)
        
        if is_active is not None:
            query = query.where(Teacher.is_active == is_active)
        
        # 최신 생성 순으로 정렬 (created_at 내림차순)
        query = query.order_by(desc(Teacher.created_at))
        query = query.offset(skip).limit(limit)
        return list(self.db.exec(query).all())

    def get_teacher(self, teacher_id: int) -> Optional[Teacher]:
        """강사 상세 조회"""
        return self.db.get(Teacher, teacher_id)

    def create_teacher(self, teacher_data: TeacherCreate) -> Teacher:
        """강사 등록"""
        # Pydantic v1 호환성을 위해 dict() 사용
        teacher = Teacher(**teacher_data.dict())
        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        return teacher

    def update_teacher(self, teacher_id: int, teacher_data: TeacherUpdate) -> Optional[Teacher]:
        """강사 정보 수정"""
        teacher = self.db.get(Teacher, teacher_id)
        if not teacher:
            return None
        
        # Pydantic v1 호환성을 위해 dict() 사용
        update_data = teacher_data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(teacher, field, value)
        
        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        return teacher

    def delete_teacher(self, teacher_id: int) -> bool:
        """강사 삭제 (소프트 삭제)"""
        teacher = self.db.get(Teacher, teacher_id)
        if not teacher:
            return False
        
        teacher.is_active = False
        teacher.updated_at = datetime.utcnow()
        
        self.db.add(teacher)
        self.db.commit()
        return True

    def hard_delete_teacher(self, teacher_id: int) -> bool:
        """강사 완전 삭제 (하드 딜리트)"""
        teacher = self.db.get(Teacher, teacher_id)
        if not teacher:
            return False
        self.db.delete(teacher)
        self.db.commit()
        return True

    def get_teacher_by_email(self, email: str) -> Optional[Teacher]:
        """이메일로 강사 조회"""
        query = select(Teacher).where(Teacher.email == email)
        return self.db.exec(query).first()

    def count_teachers(self, is_active: Optional[bool] = None) -> int:
        """강사 수 조회"""
        query = select(Teacher)
        
        if is_active is not None:
            query = query.where(Teacher.is_active == is_active)
        
        return len(self.db.exec(query).all()) 
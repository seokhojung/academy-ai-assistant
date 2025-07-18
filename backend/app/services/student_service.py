from sqlmodel import Session, select, desc
from typing import Optional
from datetime import datetime

from ..models.student import Student
from ..schemas.student import StudentCreate, StudentUpdate


class StudentService:
    def __init__(self, db: Session):
        self.db = db

    def get_students(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None
    ) -> list[Student]:
        """학생 목록 조회"""
        query = select(Student)
        
        if is_active is not None:
            query = query.where(Student.is_active == is_active)
        
        # 최신 생성 순으로 정렬 (created_at 내림차순)
        query = query.order_by(desc(Student.created_at))
        query = query.offset(skip).limit(limit)
        return list(self.db.exec(query).all())

    def get_student(self, student_id: int) -> Optional[Student]:
        """학생 상세 조회"""
        return self.db.get(Student, student_id)

    def create_student(self, student_data: StudentCreate) -> Student:
        """학생 등록"""
        # Pydantic v1 호환성을 위해 dict() 사용
        student = Student(**student_data.dict())
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def update_student(self, student_id: int, student_data: StudentUpdate) -> Optional[Student]:
        """학생 정보 수정"""
        student = self.db.get(Student, student_id)
        if not student:
            return None
        
        # Pydantic v1 호환성을 위해 dict() 사용
        update_data = student_data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(student, field, value)
        
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def delete_student(self, student_id: int) -> bool:
        """학생 삭제 (소프트 삭제)"""
        student = self.db.get(Student, student_id)
        if not student:
            return False
        
        student.is_active = False
        student.updated_at = datetime.utcnow()
        
        self.db.add(student)
        self.db.commit()
        return True

    def hard_delete_student(self, student_id: int) -> bool:
        """학생 완전 삭제 (하드 딜리트)"""
        student = self.db.get(Student, student_id)
        if not student:
            return False
        self.db.delete(student)
        self.db.commit()
        return True

    def get_student_by_email(self, email: str) -> Optional[Student]:
        """이메일로 학생 조회"""
        query = select(Student).where(Student.email == email)
        return self.db.exec(query).first()

    def count_students(self, is_active: Optional[bool] = None) -> int:
        """학생 수 조회"""
        query = select(Student)
        
        if is_active is not None:
            query = query.where(Student.is_active == is_active)
        
        return len(self.db.exec(query).all()) 
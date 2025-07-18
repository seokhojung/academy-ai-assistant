from sqlmodel import Session, select
from typing import List, Optional
from ..models.lecture import Lecture, LectureCreate, LectureUpdate
from ..schemas.lecture import LectureResponse

class LectureService:
    def __init__(self, db: Session):
        self.db = db

    def get_lectures(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[Lecture]:
        """강의 목록 조회"""
        query = select(Lecture)
        if is_active is not None:
            query = query.where(Lecture.is_active == is_active)
        query = query.offset(skip).limit(limit)
        return list(self.db.exec(query).all())

    def get_lecture(self, lecture_id: int) -> Optional[Lecture]:
        """특정 강의 조회"""
        statement = select(Lecture).where(Lecture.id == lecture_id)
        return self.db.exec(statement).first()

    def create_lecture(self, lecture_data: LectureCreate) -> Lecture:
        """새 강의 생성"""
        lecture = Lecture.from_orm(lecture_data)
        self.db.add(lecture)
        self.db.commit()
        self.db.refresh(lecture)
        return lecture

    def update_lecture(self, lecture_id: int, lecture_data: LectureUpdate) -> Optional[Lecture]:
        """강의 정보 업데이트"""
        lecture = self.get_lecture(lecture_id)
        if not lecture:
            return None
        
        update_data = lecture_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lecture, field, value)
        
        self.db.add(lecture)
        self.db.commit()
        self.db.refresh(lecture)
        return lecture

    def delete_lecture(self, lecture_id: int) -> bool:
        """강의 삭제"""
        lecture = self.get_lecture(lecture_id)
        if not lecture:
            return False
        
        self.db.delete(lecture)
        self.db.commit()
        return True

    def count_lectures(self, is_active: Optional[bool] = None) -> int:
        """강의 수 카운트"""
        query = select(Lecture)
        if is_active is not None:
            query = query.where(Lecture.is_active == is_active)
        return len(self.db.exec(query).all()) 
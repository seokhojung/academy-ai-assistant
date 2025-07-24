from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Lecture(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    subject: str = Field(index=True)
    teacher_id: Optional[int] = Field(default=None, foreign_key="teacher.id")
    material_id: Optional[int] = Field(default=None, foreign_key="material.id")
    grade: str = Field(index=True)
    max_students: int = Field(default=20)
    current_students: int = Field(default=0)
    tuition_fee: int = Field(default=0)
    schedule: str = Field(default="")  # "월수금 14:00-16:00" 형태
    classroom: str = Field(default="")
    is_active: bool = Field(default=True, index=True)
    description: Optional[str] = Field(default=None)
    
    # 새로 추가할 필드들
    difficulty_level: str = Field(default="intermediate")      # 난이도 (beginner, intermediate, advanced)
    class_duration: int = Field(default=90)                   # 수업 시간 (분)
    total_sessions: int = Field(default=16)                   # 총 수업 횟수
    completed_sessions: int = Field(default=0)                # 완료된 수업 횟수
    student_satisfaction: Optional[float] = Field(default=None)  # 학생 만족도 (1.0-5.0)
    teacher_rating: Optional[float] = Field(default=None)        # 강사 평가 (1.0-5.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LectureCreate(SQLModel):
    title: str
    subject: str
    teacher_id: Optional[int] = None
    material_id: Optional[int] = None
    grade: str
    max_students: int = 20
    tuition_fee: int = 0
    schedule: str = ""
    classroom: str = ""
    is_active: bool = True
    description: Optional[str] = None
    
    # 새로 추가할 필드들
    difficulty_level: str = "intermediate"
    class_duration: int = 90
    total_sessions: int = 16
    completed_sessions: int = 0
    student_satisfaction: Optional[float] = None
    teacher_rating: Optional[float] = None

class LectureUpdate(SQLModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    teacher_id: Optional[int] = None
    material_id: Optional[int] = None
    grade: Optional[str] = None
    max_students: Optional[int] = None
    tuition_fee: Optional[int] = None
    schedule: Optional[str] = None
    classroom: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    
    # 새로 추가할 필드들
    difficulty_level: Optional[str] = None
    class_duration: Optional[int] = None
    total_sessions: Optional[int] = None
    completed_sessions: Optional[int] = None
    student_satisfaction: Optional[float] = None
    teacher_rating: Optional[float] = None 
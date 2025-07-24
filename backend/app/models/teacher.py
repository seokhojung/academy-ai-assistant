from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
import json


class Teacher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(max_length=100, unique=True)
    phone: Optional[str] = Field(max_length=20, default=None)
    subject: str = Field(max_length=100)
    hourly_rate: float = Field(default=0.0)
    is_active: bool = Field(default=True)
    
    # 새로 추가할 필드들
    experience_years: int = Field(default=0)                    # 경력 연수
    education_level: str = Field(default="bachelor")           # 학력 (high_school, bachelor, master, phd)
    specialization: str = Field(default="")                    # 전문 분야 (예: "미적분", "독해", "실험")
    hire_date: datetime = Field(default_factory=datetime.utcnow)  # 고용일
    contract_type: str = Field(default="part_time")            # 계약 형태 (full_time, part_time, contract)
    max_lectures: int = Field(default=5)                       # 최대 담당 강의 수
    rating: Optional[float] = Field(default=None)              # 평점 (1.0-5.0)
    total_teaching_hours: int = Field(default=0)               # 총 강의 시간
    certification: str = Field(default="[]")                   # 자격증 목록 (JSON 문자열)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TeacherCreate(SQLModel):
    name: str = Field(max_length=100)
    email: str = Field(max_length=100)
    phone: Optional[str] = Field(max_length=20, default=None)
    subject: str = Field(max_length=100)
    hourly_rate: float = Field(default=0.0)
    is_active: bool = Field(default=True)
    
    # 새로 추가할 필드들
    experience_years: int = Field(default=0)
    education_level: str = Field(default="bachelor")
    specialization: str = Field(default="")
    hire_date: Optional[datetime] = Field(default=None)
    contract_type: str = Field(default="part_time")
    max_lectures: int = Field(default=5)
    rating: Optional[float] = Field(default=None)
    total_teaching_hours: int = Field(default=0)
    certification: List[str] = Field(default=[])


class TeacherUpdate(SQLModel):
    name: Optional[str] = Field(max_length=100, default=None)
    email: Optional[str] = Field(max_length=100, default=None)
    phone: Optional[str] = Field(max_length=20, default=None)
    subject: Optional[str] = Field(max_length=100, default=None)
    hourly_rate: Optional[float] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    
    # 새로 추가할 필드들
    experience_years: Optional[int] = Field(default=None)
    education_level: Optional[str] = Field(default=None)
    specialization: Optional[str] = Field(default=None)
    hire_date: Optional[datetime] = Field(default=None)
    contract_type: Optional[str] = Field(default=None)
    max_lectures: Optional[int] = Field(default=None)
    rating: Optional[float] = Field(default=None)
    total_teaching_hours: Optional[int] = Field(default=None)
    certification: Optional[List[str]] = Field(default=None) 
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.lecture import Lecture
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.material import Material
from typing import Dict, Any

router = APIRouter()

@router.post("/init-sample-data")
def init_sample_data(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """배포 환경에 샘플 데이터 초기화"""
    try:
        # 강사 데이터 추가
        teachers_data = [
            Teacher(name="김수학", subject="수학", email="kim.math@academy.com", phone="010-1234-5678"),
            Teacher(name="이영어", subject="영어", email="lee.english@academy.com", phone="010-2345-6789"),
            Teacher(name="박과학", subject="과학", email="park.science@academy.com", phone="010-3456-7890"),
            Teacher(name="최국어", subject="국어", email="choi.korean@academy.com", phone="010-4567-8901"),
        ]
        
        for teacher in teachers_data:
            existing = session.exec(select(Teacher).where(Teacher.email == teacher.email)).first()
            if not existing:
                session.add(teacher)
        
        session.commit()
        
        # 교재 데이터 추가 (publisher 필드 제거)
        materials_data = [
            Material(name="중등 수학 기초", subject="수학", grade="중1", author="김수학"),
            Material(name="고등 영어 독해", subject="영어", grade="고1", author="이영어"),
            Material(name="중등 과학 실험", subject="과학", grade="중2", author="박과학"),
            Material(name="고등 국어 문학", subject="국어", grade="고2", author="최국어"),
        ]
        
        for material in materials_data:
            existing = session.exec(select(Material).where(Material.name == material.name)).first()
            if not existing:
                session.add(material)
        
        session.commit()
        
        # 학생 데이터 추가
        students_data = [
            Student(name="김학생", grade="중1", email="kim.student@email.com", phone="010-1111-2222"),
            Student(name="이학생", grade="고1", email="lee.student@email.com", phone="010-2222-3333"),
            Student(name="박학생", grade="중2", email="park.student@email.com", phone="010-3333-4444"),
            Student(name="최학생", grade="고2", email="choi.student@email.com", phone="010-4444-5555"),
        ]
        
        for student in students_data:
            existing = session.exec(select(Student).where(Student.email == student.email)).first()
            if not existing:
                session.add(student)
        
        session.commit()
        
        # 강의 데이터 추가
        lectures_data = [
            Lecture(title="중등 수학 기초반", subject="수학", grade="중1", max_students=15, current_students=8, tuition_fee=150000, schedule="월수금 14:00-16:00", classroom="A-101", is_active=True, description="중학교 1학년 수학 기초 과정"),
            Lecture(title="고등 영어 독해반", subject="영어", grade="고1", max_students=12, current_students=10, tuition_fee=180000, schedule="화목 16:00-18:00", classroom="B-201", is_active=True, description="고등학교 1학년 영어 독해 과정"),
            Lecture(title="중등 과학 실험반", subject="과학", grade="중2", max_students=10, current_students=6, tuition_fee=200000, schedule="토 10:00-12:00", classroom="실험실-1", is_active=True, description="중학교 2학년 과학 실험 과정"),
            Lecture(title="고등 국어 문학반", subject="국어", grade="고2", max_students=15, current_students=12, tuition_fee=160000, schedule="월수 19:00-21:00", classroom="C-301", is_active=True, description="고등학교 2학년 국어 문학 과정"),
        ]
        
        for lecture in lectures_data:
            existing = session.exec(select(Lecture).where(Lecture.title == lecture.title)).first()
            if not existing:
                session.add(lecture)
        
        session.commit()
        
        # 데이터 확인
        teacher_count = len(session.exec(select(Teacher)).all())
        material_count = len(session.exec(select(Material)).all())
        student_count = len(session.exec(select(Student)).all())
        lecture_count = len(session.exec(select(Lecture)).all())
        
        return {
            "success": True,
            "message": "샘플 데이터가 성공적으로 추가되었습니다!",
            "data": {
                "teachers": teacher_count,
                "materials": material_count,
                "students": student_count,
                "lectures": lecture_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 추가 중 오류 발생: {str(e)}") 
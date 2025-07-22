#!/usr/bin/env python3
"""
데이터베이스 데이터 확인 스크립트
"""

import asyncio
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.material import Material
from app.models.lecture import Lecture

async def check_database_data():
    """데이터베이스 데이터 확인"""
    
    print("=" * 60)
    print("🗄️ 데이터베이스 데이터 확인")
    print("=" * 60)
    
    try:
        session = next(get_session())
        
        # 학생 데이터 확인
        students = session.query(Student).all()
        print(f"\n👥 학생 데이터: {len(students)}명")
        if students:
            print("최근 3명:")
            for i, student in enumerate(students[:3]):
                print(f"  {i+1}. {student.name} (학년: {student.grade}, 이메일: {student.email})")
        
        # 강사 데이터 확인
        teachers = session.query(Teacher).all()
        print(f"\n👨‍🏫 강사 데이터: {len(teachers)}명")
        if teachers:
            print("최근 3명:")
            for i, teacher in enumerate(teachers[:3]):
                print(f"  {i+1}. {teacher.name} (과목: {teacher.subject}, 이메일: {teacher.email})")
        
        # 교재 데이터 확인
        materials = session.query(Material).all()
        print(f"\n📚 교재 데이터: {len(materials)}개")
        if materials:
            print("최근 3개:")
            for i, material in enumerate(materials[:3]):
                print(f"  {i+1}. {material.name} (과목: {material.subject}, 출판사: {material.publisher})")
        
        # 강의 데이터 확인
        lectures = session.query(Lecture).all()
        print(f"\n📖 강의 데이터: {len(lectures)}개")
        if lectures:
            print("최근 3개:")
            for i, lecture in enumerate(lectures[:3]):
                print(f"  {i+1}. {lecture.title} (과목: {lecture.subject}, 강의실: {lecture.classroom})")
        
        # 전체 통계
        print(f"\n📊 전체 통계:")
        print(f"  - 학생: {len(students)}명")
        print(f"  - 강사: {len(teachers)}명")
        print(f"  - 교재: {len(materials)}개")
        print(f"  - 강의: {len(lectures)}개")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(check_database_data()) 
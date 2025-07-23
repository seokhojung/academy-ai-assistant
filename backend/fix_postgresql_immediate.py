#!/usr/bin/env python3
"""
PostgreSQL 데이터 즉시 수정 스크립트
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def fix_postgresql_data():
    """PostgreSQL 데이터 즉시 수정"""
    
    # 환경변수에서 데이터베이스 URL 가져오기
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        # SQLAlchemy 엔진 생성
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        print("🔧 PostgreSQL 데이터 즉시 수정 시작...")
        
        with SessionLocal() as session:
            # 1. 기존 데이터 삭제
            print("  🗑️ 기존 데이터 삭제...")
            tables = ['lecture', 'material', 'student', 'teacher']
            for table in tables:
                session.execute(text(f"DELETE FROM {table}"))
                print(f"    ✅ {table} 테이블 데이터 삭제")
            
            session.commit()
        
                    # 2. 샘플 데이터 삽입 (boolean 타입으로)
            print("  📝 샘플 데이터 삽입...")
            
            # 학생 데이터
            students = [
                ("김철수", "kim@academy.com", "010-1234-5678", "고1", 500000, True),
                ("이영희", "lee@academy.com", "010-2345-6789", "고2", 600000, True),
                ("박민수", "park@academy.com", "010-3456-7890", "고3", 700000, True),
                ("최지영", "choi@academy.com", "010-4567-8901", "중1", 400000, True),
                ("정현우", "jung@academy.com", "010-5678-9012", "중2", 450000, True),
            ]
            
            for student in students:
                session.execute(text("""
                    INSERT INTO student (name, email, phone, grade, tuition_fee, is_active)
                    VALUES (:name, :email, :phone, :grade, :tuition_fee, :is_active)
                """), {
                    'name': student[0],
                    'email': student[1],
                    'phone': student[2],
                    'grade': student[3],
                    'tuition_fee': student[4],
                    'is_active': student[5]
                })
            
            print(f"    ✅ 학생 {len(students)}명 추가")
            
            # 강사 데이터
            teachers = [
                ("김수학", "math@academy.com", "010-1111-2222", "수학", 50000, True),
                ("이영어", "english@academy.com", "010-3333-4444", "영어", 45000, True),
                ("박과학", "science@academy.com", "010-5555-6666", "과학", 48000, True),
                ("최국어", "korean@academy.com", "010-7777-8888", "국어", 42000, True),
                ("정사회", "social@academy.com", "010-9999-0000", "사회", 40000, True),
            ]
            
            for teacher in teachers:
                session.execute(text("""
                    INSERT INTO teacher (name, email, phone, subject, hourly_rate, is_active)
                    VALUES (:name, :email, :phone, :subject, :hourly_rate, :is_active)
                """), {
                    'name': teacher[0],
                    'email': teacher[1],
                    'phone': teacher[2],
                    'subject': teacher[3],
                    'hourly_rate': teacher[4],
                    'is_active': teacher[5]
                })
            
            print(f"    ✅ 강사 {len(teachers)}명 추가")
            
            # 교재 데이터
            materials = [
                ("중등 수학 1", "수학", "중1", "미래엔", "김수학", "978-89-408-1234-5", 30, 15000, True),
                ("고등 영어 독해", "영어", "고1", "YBM", "이영어", "978-89-408-1236-9", 25, 20000, True),
                ("중등 과학 실험", "과학", "중3", "비상교육", "박과학", "978-89-408-1237-6", 20, 18000, True),
                ("고등 국어 문학", "국어", "고2", "두산동아", "최국어", "978-89-408-1238-3", 15, 22000, True),
                ("중등 사회 탐구", "사회", "중2", "지학사", "정사회", "978-89-408-1239-0", 18, 16000, True),
            ]
            
            for material in materials:
                session.execute(text("""
                    INSERT INTO material (name, subject, grade, publisher, author, isbn, quantity, price, is_active)
                    VALUES (:name, :subject, :grade, :publisher, :author, :isbn, :quantity, :price, :is_active)
                """), {
                    'name': material[0],
                    'subject': material[1],
                    'grade': material[2],
                    'publisher': material[3],
                    'author': material[4],
                    'isbn': material[5],
                    'quantity': material[6],
                    'price': material[7],
                    'is_active': material[8]
                })
            
            print(f"    ✅ 교재 {len(materials)}개 추가")
            
            # 강의 데이터
            lectures = [
                ("고1 수학 기초", "수학", "고1", 15, 8, 150000, "월수금 14:00-16:00", "A-101", True),
                ("고2 영어 독해", "영어", "고2", 12, 10, 180000, "화목 15:00-17:00", "B-201", True),
                ("중3 과학 실험", "과학", "중3", 10, 6, 200000, "토 10:00-12:00", "실험실-1", True),
                ("고2 국어 문학", "국어", "고2", 15, 12, 160000, "월수 19:00-21:00", "C-301", True),
                ("중2 사회 탐구", "사회", "중2", 12, 9, 140000, "화목 15:00-17:00", "A-102", True),
            ]
            
            for lecture in lectures:
                session.execute(text("""
                    INSERT INTO lecture (title, subject, grade, max_students, current_students, tuition_fee, schedule, classroom, is_active)
                    VALUES (:title, :subject, :grade, :max_students, :current_students, :tuition_fee, :schedule, :classroom, :is_active)
                """), {
                    'title': lecture[0],
                    'subject': lecture[1],
                    'grade': lecture[2],
                    'max_students': lecture[3],
                    'current_students': lecture[4],
                    'tuition_fee': lecture[5],
                    'schedule': lecture[6],
                    'classroom': lecture[7],
                    'is_active': lecture[8]
                })
            
            print(f"    ✅ 강의 {len(lectures)}개 추가")
            
            session.commit()
            
            # 3. 결과 확인
            print("  📊 데이터 확인...")
            for table in ['student', 'teacher', 'material', 'lecture']:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"    {table}: {count}개")
        
        print("✅ PostgreSQL 데이터 수정 완료!")
        
    except Exception as e:
        print(f"❌ PostgreSQL 데이터 수정 실패: {e}")
        if 'session' in locals():
            session.rollback()

if __name__ == "__main__":
    fix_postgresql_data() 
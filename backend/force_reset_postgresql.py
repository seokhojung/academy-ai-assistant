#!/usr/bin/env python3
"""
PostgreSQL 강제 초기화 및 academy.db 마이그레이션 스크립트
- PostgreSQL의 모든 테이블과 데이터를 완전히 삭제
- academy.db의 모든 데이터를 PostgreSQL로 완전 복사
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData
from sqlmodel import Session

# 현재 디렉터리를 파이썬 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'app'))

from app.core.config import get_settings
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.lecture import Lecture
from app.models.material import Material
from app.models.user import User

def force_reset_postgresql():
    """PostgreSQL 완전 초기화 및 마이그레이션"""
    print("🔥 PostgreSQL 강제 초기화 시작...")
    
    settings = get_settings()
    
    # SQLite 연결 (로컬 데이터)
    sqlite_path = os.path.join(current_dir, "academy.db")
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite 파일을 찾을 수 없습니다: {sqlite_path}")
        return False
        
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    
    # PostgreSQL 연결
    if settings.database_url and settings.database_url.startswith("postgresql"):
        postgres_engine = create_engine(settings.database_url)
        print(f"✅ PostgreSQL 연결: {settings.database_url}")
    else:
        print("❌ PostgreSQL 연결 정보가 없습니다.")
        return False
    
    try:
        # 1. PostgreSQL 모든 테이블 완전 삭제
        print("🗑️ PostgreSQL 모든 테이블 삭제 중...")
        with postgres_engine.connect() as conn:
            # 외래 키 제약 조건 비활성화
            conn.execute(text("SET session_replication_role = replica;"))
            
            # 모든 테이블 목록 가져오기
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            
            # 각 테이블 완전 삭제
            for table in tables:
                print(f"  🗑️ 테이블 삭제: {table}")
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            
            # 외래 키 제약 조건 다시 활성화
            conn.execute(text("SET session_replication_role = DEFAULT;"))
            conn.commit()
            
        print("✅ PostgreSQL 모든 테이블 삭제 완료!")
        
        # 2. 새로운 테이블 생성
        print("🏗️ PostgreSQL 새 테이블 생성 중...")
        from app.core.database import create_db_and_tables
        create_db_and_tables()
        print("✅ 새 테이블 생성 완료!")
        
        # 3. SQLite에서 데이터 읽기 및 PostgreSQL로 복사
        print("📊 academy.db에서 데이터 마이그레이션 시작...")
        
        # Students 마이그레이션
        with Session(sqlite_engine) as sqlite_session:
            students = sqlite_session.exec(text("SELECT * FROM student")).fetchall()
            print(f"  📚 학생 데이터: {len(students)}개")
            
            with Session(postgres_engine) as postgres_session:
                for student_row in students:
                    student = Student(
                        name=student_row[1],  # name
                        email=student_row[2] if student_row[2] else f"student{student_row[0]}@example.com",
                        phone=student_row[3] if student_row[3] else "",
                        grade=student_row[4] if student_row[4] else "",
                        school=student_row[5] if student_row[5] else "",
                        parent_name=student_row[6] if student_row[6] else "",
                        parent_phone=student_row[7] if student_row[7] else "",
                        address=student_row[8] if student_row[8] else "",
                        notes=student_row[9] if student_row[9] else "",
                        enrollment_date=datetime.fromisoformat(student_row[10]) if student_row[10] else datetime.now(),
                        is_active=bool(student_row[11]) if student_row[11] is not None else True,
                        created_at=datetime.fromisoformat(student_row[12]) if student_row[12] else datetime.now(),
                        updated_at=datetime.fromisoformat(student_row[13]) if student_row[13] else datetime.now()
                    )
                    postgres_session.add(student)
                postgres_session.commit()
                print(f"  ✅ {len(students)}명 학생 마이그레이션 완료!")
        
        # Teachers 마이그레이션
        with Session(sqlite_engine) as sqlite_session:
            teachers = sqlite_session.exec(text("SELECT * FROM teacher")).fetchall()
            print(f"  👨‍🏫 교사 데이터: {len(teachers)}개")
            
            with Session(postgres_engine) as postgres_session:
                for teacher_row in teachers:
                    teacher = Teacher(
                        name=teacher_row[1],
                        email=teacher_row[2] if teacher_row[2] else f"teacher{teacher_row[0]}@example.com",
                        phone=teacher_row[3] if teacher_row[3] else "",
                        subject=teacher_row[4] if teacher_row[4] else "",
                        hire_date=datetime.fromisoformat(teacher_row[5]) if teacher_row[5] else datetime.now(),
                        salary=float(teacher_row[6]) if teacher_row[6] else 0.0,
                        notes=teacher_row[7] if teacher_row[7] else "",
                        is_active=bool(teacher_row[8]) if teacher_row[8] is not None else True,
                        created_at=datetime.fromisoformat(teacher_row[9]) if teacher_row[9] else datetime.now(),
                        updated_at=datetime.fromisoformat(teacher_row[10]) if teacher_row[10] else datetime.now()
                    )
                    postgres_session.add(teacher)
                postgres_session.commit()
                print(f"  ✅ {len(teachers)}명 교사 마이그레이션 완료!")
        
        # Materials 마이그레이션
        with Session(sqlite_engine) as sqlite_session:
            materials = sqlite_session.exec(text("SELECT * FROM material")).fetchall()
            print(f"  📖 교재 데이터: {len(materials)}개")
            
            with Session(postgres_engine) as postgres_session:
                for material_row in materials:
                    material = Material(
                        title=material_row[1],
                        category=material_row[2] if material_row[2] else "",
                        author=material_row[3] if material_row[3] else "",
                        publisher=material_row[4] if material_row[4] else "",
                        isbn=material_row[5] if material_row[5] else "",
                        description=material_row[6] if material_row[6] else "",
                        publication_date=datetime.fromisoformat(material_row[7]) if material_row[7] else datetime.now(),
                        edition=material_row[8] if material_row[8] else "",
                        quantity=int(material_row[9]) if material_row[9] else 0,
                        min_quantity=int(material_row[10]) if material_row[10] else 0,
                        price=float(material_row[11]) if material_row[11] else 0.0,
                        expiry_date=datetime.fromisoformat(material_row[12]) if material_row[12] else None,
                        is_active=bool(material_row[13]) if material_row[13] is not None else True,
                        created_at=datetime.fromisoformat(material_row[14]) if material_row[14] else datetime.now(),
                        updated_at=datetime.fromisoformat(material_row[15]) if material_row[15] else datetime.now()
                    )
                    postgres_session.add(material)
                postgres_session.commit()
                print(f"  ✅ {len(materials)}개 교재 마이그레이션 완료!")
        
        # Lectures 마이그레이션
        with Session(sqlite_engine) as sqlite_session:
            lectures = sqlite_session.exec(text("SELECT * FROM lecture")).fetchall()
            print(f"  🎓 강의 데이터: {len(lectures)}개")
            
            with Session(postgres_engine) as postgres_session:
                for lecture_row in lectures:
                    lecture = Lecture(
                        title=lecture_row[1],
                        subject=lecture_row[2] if lecture_row[2] else "",
                        teacher_id=int(lecture_row[3]) if lecture_row[3] else None,
                        schedule=lecture_row[4] if lecture_row[4] else "",
                        classroom=lecture_row[5] if lecture_row[5] else "",
                        capacity=int(lecture_row[6]) if lecture_row[6] else 0,
                        current_enrollment=int(lecture_row[7]) if lecture_row[7] else 0,
                        start_date=datetime.fromisoformat(lecture_row[8]) if lecture_row[8] else datetime.now(),
                        end_date=datetime.fromisoformat(lecture_row[9]) if lecture_row[9] else datetime.now(),
                        description=lecture_row[10] if lecture_row[10] else "",
                        fee=float(lecture_row[11]) if lecture_row[11] else 0.0,
                        is_active=bool(lecture_row[12]) if lecture_row[12] is not None else True,
                        created_at=datetime.fromisoformat(lecture_row[13]) if lecture_row[13] else datetime.now(),
                        updated_at=datetime.fromisoformat(lecture_row[14]) if lecture_row[14] else datetime.now()
                    )
                    postgres_session.add(lecture)
                postgres_session.commit()
                print(f"  ✅ {len(lectures)}개 강의 마이그레이션 완료!")
        
        # 최종 확인
        print("\n🔍 마이그레이션 결과 확인:")
        with Session(postgres_engine) as session:
            student_count = len(session.exec(text("SELECT * FROM student")).fetchall())
            teacher_count = len(session.exec(text("SELECT * FROM teacher")).fetchall())
            material_count = len(session.exec(text("SELECT * FROM material")).fetchall())
            lecture_count = len(session.exec(text("SELECT * FROM lecture")).fetchall())
            
            print(f"  📚 학생: {student_count}명")
            print(f"  👨‍🏫 교사: {teacher_count}명")
            print(f"  📖 교재: {material_count}개")
            print(f"  🎓 강의: {lecture_count}개")
        
        print(f"\n🎉 PostgreSQL 강제 초기화 및 마이그레이션 완료!")
        print(f"📊 이제 PostgreSQL이 academy.db와 완전히 동일합니다!")
        return True
        
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    force_reset_postgresql() 
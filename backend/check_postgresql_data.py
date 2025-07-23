#!/usr/bin/env python3
"""
PostgreSQL 데이터 직접 확인 스크립트
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def check_postgresql_data():
    """PostgreSQL 데이터 확인"""
    
    # 환경 변수에서 데이터베이스 URL 가져오기
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
        return
    
    if "sqlite" in database_url:
        print("❌ SQLite 데이터베이스입니다. PostgreSQL을 확인해주세요.")
        return
    
    try:
        print("🔍 PostgreSQL 데이터 확인 시작...")
        print(f"📊 데이터베이스 URL: {database_url}")
        
        # 엔진 생성
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # 테이블 목록 확인
            print("\n📋 테이블 목록:")
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            for table in tables:
                print(f"  - {table}")
            
            # 각 테이블의 데이터 개수 확인
            print("\n📊 데이터 개수:")
            for table in ['student', 'teacher', 'material', 'lecture', 'user']:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  {table}: {count}개")
                except Exception as e:
                    print(f"  {table}: 확인 실패 - {e}")
            
            # 학생 데이터 샘플 확인
            print("\n👥 학생 데이터 샘플:")
            try:
                result = session.execute(text("SELECT id, name, email, grade, is_active FROM student LIMIT 5"))
                students = result.fetchall()
                for student in students:
                    print(f"  ID: {student[0]}, 이름: {student[1]}, 이메일: {student[2]}, 학년: {student[3]}, 활성: {student[4]}")
            except Exception as e:
                print(f"  학생 데이터 확인 실패: {e}")
            
            # 강사 데이터 샘플 확인
            print("\n👨‍🏫 강사 데이터 샘플:")
            try:
                result = session.execute(text("SELECT id, name, email, subject, is_active FROM teacher LIMIT 5"))
                teachers = result.fetchall()
                for teacher in teachers:
                    print(f"  ID: {teacher[0]}, 이름: {teacher[1]}, 이메일: {teacher[2]}, 과목: {teacher[3]}, 활성: {teacher[4]}")
            except Exception as e:
                print(f"  강사 데이터 확인 실패: {e}")
            
            # 교재 데이터 샘플 확인
            print("\n📚 교재 데이터 샘플:")
            try:
                result = session.execute(text("SELECT id, name, subject, grade, author, is_active FROM material LIMIT 5"))
                materials = result.fetchall()
                for material in materials:
                    print(f"  ID: {material[0]}, 이름: {material[1]}, 과목: {material[2]}, 학년: {material[3]}, 저자: {material[4]}, 활성: {material[5]}")
            except Exception as e:
                print(f"  교재 데이터 확인 실패: {e}")
            
            # 강의 데이터 샘플 확인
            print("\n🎓 강의 데이터 샘플:")
            try:
                result = session.execute(text("SELECT id, title, subject, grade, is_active FROM lecture LIMIT 5"))
                lectures = result.fetchall()
                for lecture in lectures:
                    print(f"  ID: {lecture[0]}, 제목: {lecture[1]}, 과목: {lecture[2]}, 학년: {lecture[3]}, 활성: {lecture[4]}")
            except Exception as e:
                print(f"  강의 데이터 확인 실패: {e}")
        
        print("\n✅ PostgreSQL 데이터 확인 완료!")
        
    except Exception as e:
        print(f"❌ PostgreSQL 데이터 확인 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_postgresql_data() 
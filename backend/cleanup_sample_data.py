#!/usr/bin/env python3
"""
샘플 데이터 정리 스크립트
기존에 추가된 개같은 샘플 데이터를 삭제하고 실제 데이터만 남김
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def cleanup_sample_data():
    """샘플 데이터 정리"""
    
    # 환경 변수에서 데이터베이스 URL 가져오기
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # 로컬 테스트용 - 직접 PostgreSQL URL 사용
        database_url = "postgresql://academy_user:academy_password@localhost:5432/academy_db"
        print("⚠️ DATABASE_URL 환경 변수가 없어 로컬 PostgreSQL 사용")
    
    if "sqlite" in database_url:
        print("❌ SQLite는 정리 대상이 아닙니다. PostgreSQL만 정리합니다.")
        return
    
    try:
        print("🧹 샘플 데이터 정리 시작...")
        print(f"📊 데이터베이스 URL: {database_url}")
        
        # 엔진 생성
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # 1. 현재 데이터 현황 확인
            print("\n📊 현재 데이터 현황:")
            for table in ['student', 'teacher', 'material', 'lecture']:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  {table}: {count}개")
                except Exception as e:
                    print(f"  {table}: 확인 실패 - {e}")
            
            # 2. 샘플 데이터 패턴 확인
            print("\n🔍 샘플 데이터 패턴 확인:")
            
            # 김철수, 이영희, 박민수 같은 명백한 샘플 데이터 찾기
            sample_student_emails = [
                'kim@academy.com', 'lee@academy.com', 'park@academy.com',
                'math@academy.com', 'english@academy.com', 'science@academy.com'
            ]
            
            # 3. 샘플 학생 삭제
            print("\n🗑️ 샘플 학생 데이터 삭제:")
            for email in sample_student_emails:
                try:
                    result = session.execute(text("SELECT COUNT(*) FROM student WHERE email = :email"), {"email": email})
                    count = result.scalar()
                    if count > 0:
                        session.execute(text("DELETE FROM student WHERE email = :email"), {"email": email})
                        print(f"  삭제: {email} ({count}개)")
                except Exception as e:
                    print(f"  오류: {email} - {e}")
            
            # 4. 샘플 강사 삭제
            print("\n🗑️ 샘플 강사 데이터 삭제:")
            sample_teacher_emails = [
                'math@academy.com', 'english@academy.com', 'science@academy.com',
                'kim.math@academy.com', 'lee.english@academy.com', 'park.science@academy.com'
            ]
            
            for email in sample_teacher_emails:
                try:
                    result = session.execute(text("SELECT COUNT(*) FROM teacher WHERE email = :email"), {"email": email})
                    count = result.scalar()
                    if count > 0:
                        session.execute(text("DELETE FROM teacher WHERE email = :email"), {"email": email})
                        print(f"  삭제: {email} ({count}개)")
                except Exception as e:
                    print(f"  오류: {email} - {e}")
            
            # 5. 샘플 교재 삭제 (특정 패턴)
            print("\n🗑️ 샘플 교재 데이터 삭제:")
            sample_materials = ["중등 수학 1", "고등 영어 독해", "중등 과학 실험"]
            
            for material_name in sample_materials:
                try:
                    result = session.execute(text("SELECT COUNT(*) FROM material WHERE name = :name"), {"name": material_name})
                    count = result.scalar()
                    if count > 0:
                        session.execute(text("DELETE FROM material WHERE name = :name"), {"name": material_name})
                        print(f"  삭제: {material_name} ({count}개)")
                except Exception as e:
                    print(f"  오류: {material_name} - {e}")
            
            # 6. 샘플 강의 삭제
            print("\n🗑️ 샘플 강의 데이터 삭제:")
            sample_lectures = ["고1 수학 기초", "고2 영어 독해", "중3 과학 실험"]
            
            for lecture_title in sample_lectures:
                try:
                    result = session.execute(text("SELECT COUNT(*) FROM lecture WHERE title = :title"), {"title": lecture_title})
                    count = result.scalar()
                    if count > 0:
                        session.execute(text("DELETE FROM lecture WHERE title = :title"), {"title": lecture_title})
                        print(f"  삭제: {lecture_title} ({count}개)")
                except Exception as e:
                    print(f"  오류: {lecture_title} - {e}")
            
            # 변경사항 커밋
            session.commit()
            
            # 7. 정리 후 데이터 현황 확인
            print("\n📊 정리 후 데이터 현황:")
            for table in ['student', 'teacher', 'material', 'lecture']:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  {table}: {count}개")
                except Exception as e:
                    print(f"  {table}: 확인 실패 - {e}")
        
        print("\n✅ 샘플 데이터 정리 완료!")
        print("🎯 이제 실제 로컬 데이터만 남았습니다.")
        
    except Exception as e:
        print(f"❌ 샘플 데이터 정리 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    cleanup_sample_data() 
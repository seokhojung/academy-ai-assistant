#!/usr/bin/env python3
"""
직접 테이블 생성 스크립트
"""

import os
import sys
from sqlmodel import SQLModel, create_engine, Session
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.lecture import Lecture
from app.models.material import Material
from app.models.user import User

def create_tables_direct():
    """직접 테이블 생성"""
    print("=== 직접 테이블 생성 시작 ===")
    
    # DB URL 설정
    db_url = "sqlite:///./academy.db"
    print(f"[DEBUG] DB URL: {db_url}")
    
    # 엔진 생성
    engine = create_engine(db_url, echo=True)
    
    try:
        # 모든 모델을 포함하여 테이블 생성
        SQLModel.metadata.create_all(engine)
        print("✅ 모든 테이블 생성 완료")
        
        # 테이블 존재 확인
        with Session(engine) as session:
            # 각 테이블에 대해 간단한 쿼리 실행
            try:
                teachers = session.exec("SELECT COUNT(*) FROM teacher").first()
                print(f"✅ teacher 테이블 확인: {teachers}개 레코드")
            except Exception as e:
                print(f"❌ teacher 테이블 오류: {e}")
            
            try:
                students = session.exec("SELECT COUNT(*) FROM student").first()
                print(f"✅ student 테이블 확인: {students}개 레코드")
            except Exception as e:
                print(f"❌ student 테이블 오류: {e}")
            
            try:
                lectures = session.exec("SELECT COUNT(*) FROM lecture").first()
                print(f"✅ lecture 테이블 확인: {lectures}개 레코드")
            except Exception as e:
                print(f"❌ lecture 테이블 오류: {e}")
            
            try:
                materials = session.exec("SELECT COUNT(*) FROM material").first()
                print(f"✅ material 테이블 확인: {materials}개 레코드")
            except Exception as e:
                print(f"❌ material 테이블 오류: {e}")
            
            try:
                users = session.exec("SELECT COUNT(*) FROM user").first()
                print(f"✅ user 테이블 확인: {users}개 레코드")
            except Exception as e:
                print(f"❌ user 테이블 오류: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_tables_direct() 
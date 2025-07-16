#!/usr/bin/env python3
"""
PostgreSQL 연결 테스트 스크립트
"""

import os
import sys
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

def test_postgresql_connection():
    """PostgreSQL 연결 테스트"""
    print("=== PostgreSQL 연결 테스트 ===")
    
    try:
        # 데이터베이스 URL 확인
        print(f"데이터베이스 URL: {settings.database_url}")
        
        # PostgreSQL 엔진 생성
        print("PostgreSQL 엔진 생성 중...")
        engine = create_engine(
            settings.database_url,
            echo=True,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # 연결 테스트
        print("데이터베이스 연결 테스트 중...")
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("SELECT version();"))
            row = result.fetchone()
            if row:
                version = row[0]
                print(f"PostgreSQL 버전: {version}")
            else:
                print("버전 정보를 가져올 수 없습니다.")
        
        # 테이블 생성 테스트
        print("테이블 생성 테스트 중...")
        SQLModel.metadata.create_all(engine)
        print("테이블 생성 성공!")
        
        # 세션 테스트
        print("세션 테스트 중...")
        with Session(engine) as session:
            # 간단한 쿼리 실행
            from sqlalchemy import text
            result = session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row:
                test_value = row[0]
                print(f"테스트 쿼리 결과: {test_value}")
            else:
                print("테스트 쿼리 결과를 가져올 수 없습니다.")
        
        print("✅ PostgreSQL 연결 테스트 성공!")
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL 연결 테스트 실패: {e}")
        return False

def check_environment_variables():
    """환경 변수 확인"""
    print("=== 환경 변수 확인 ===")
    
    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "FIREBASE_API_KEY",
        "GEMINI_API_KEY"
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 민감한 정보는 일부만 표시
            if "password" in var.lower() or "key" in var.lower():
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: 설정되지 않음")
    
    print()

if __name__ == "__main__":
    # 환경 변수 확인
    check_environment_variables()
    
    # PostgreSQL 연결 테스트
    success = test_postgresql_connection()
    
    if success:
        print("\n🎉 PostgreSQL 설정이 완료되었습니다!")
        print("이제 애플리케이션을 실행할 수 있습니다.")
    else:
        print("\n⚠️ PostgreSQL 설정에 문제가 있습니다.")
        print("환경 변수와 연결 정보를 확인해주세요.")
        sys.exit(1) 
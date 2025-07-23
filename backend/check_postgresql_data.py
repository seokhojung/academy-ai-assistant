#!/usr/bin/env python3
"""
PostgreSQL 데이터 확인 스크립트
현재 PostgreSQL에 저장된 실제 데이터를 확인합니다.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 환경 변수에서 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    print("로컬에서 실행하려면 .env 파일의 DATABASE_URL을 확인하세요.")
    sys.exit(1)

def check_postgresql_data():
    """PostgreSQL 데이터 확인"""
    try:
        print("🔍 PostgreSQL 데이터 확인 시작...")
        print(f"데이터베이스 URL: {DATABASE_URL[:50]}...")
        
        # 엔진 생성
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # 세션 생성
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            print("\n" + "="*50)
            print("📊 현재 데이터베이스 상태")
            print("="*50)
            
            # 1. 테이블 존재 여부 확인
            print("\n1️⃣ 테이블 존재 여부 확인...")
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"  발견된 테이블: {tables}")
            
            # 2. 각 테이블의 데이터 수 확인
            print("\n2️⃣ 각 테이블의 데이터 수 확인...")
            
            for table in ['student', 'teacher', 'material', 'lecture']:
                if table in tables:
                    try:
                        result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        print(f"  {table}: {count}개")
                        
                        # 처음 3개 레코드 출력
                        if count > 0:
                            result = session.execute(text(f"SELECT * FROM {table} LIMIT 3"))
                            rows = result.fetchall()
                            print(f"    샘플 데이터:")
                            for i, row in enumerate(rows, 1):
                                print(f"      {i}. {row}")
                    except Exception as e:
                        print(f"  {table}: 오류 - {e}")
                else:
                    print(f"  {table}: 테이블이 존재하지 않음")
            
            # 3. material 테이블 컬럼 확인
            print("\n3️⃣ material 테이블 컬럼 확인...")
            try:
                result = session.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'material'
                    ORDER BY ordinal_position;
                """))
                
                columns = []
                for row in result.fetchall():
                    columns.append(row[0])
                    print(f"  - {row[0]} ({row[1]}, nullable: {row[2]})")
                
                print(f"\n  총 {len(columns)}개 컬럼")
                
                # 필수 컬럼 확인
                required_columns = ['id', 'name', 'subject', 'grade', 'author']
                missing_required = [col for col in required_columns if col not in columns]
                
                if missing_required:
                    print(f"  ❌ 누락된 필수 컬럼: {missing_required}")
                else:
                    print(f"  ✅ 모든 필수 컬럼 존재")
                    
            except Exception as e:
                print(f"  ❌ material 테이블 컬럼 확인 실패: {e}")
            
            # 4. 데이터 상세 확인
            print("\n4️⃣ 데이터 상세 확인...")
            
            for table in ['student', 'teacher', 'material', 'lecture']:
                if table in tables:
                    try:
                        result = session.execute(text(f"SELECT * FROM {table}"))
                        rows = result.fetchall()
                        
                        if rows:
                            print(f"\n  📋 {table} 테이블 전체 데이터 ({len(rows)}개):")
                            for i, row in enumerate(rows, 1):
                                print(f"    {i}. {row}")
                        else:
                            print(f"\n  📋 {table} 테이블: 데이터 없음")
                            
                    except Exception as e:
                        print(f"\n  ❌ {table} 테이블 조회 실패: {e}")
            
            print("\n" + "="*50)
            print("✅ 데이터 확인 완료")
            print("="*50)
                
    except Exception as e:
        print(f"❌ 데이터 확인 중 오류: {e}")

if __name__ == "__main__":
    print("🚀 PostgreSQL 데이터 확인 스크립트 시작")
    check_postgresql_data() 
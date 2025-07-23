#!/usr/bin/env python3
"""
PostgreSQL 스키마 확인 및 수정 스크립트
"""

import os
import sys
from sqlmodel import SQLModel, create_engine, Session, text
from app.core.config import settings
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.material import Material
from app.models.lecture import Lecture

def check_postgresql_schema():
    """PostgreSQL 스키마 확인 및 수정"""
    print("=== PostgreSQL 스키마 확인 및 수정 ===")
    
    # PostgreSQL 엔진 생성
    pg_engine = create_engine(
        settings.database_url,
        echo=True,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    try:
        with Session(pg_engine) as session:
            # 1. 테이블 존재 확인
            print("\n1. 테이블 존재 확인...")
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"존재하는 테이블: {tables}")
            
            # 2. material 테이블 컬럼 확인
            print("\n2. material 테이블 컬럼 확인...")
            result = session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'material'
                ORDER BY ordinal_position;
            """))
            columns = result.fetchall()
            print("material 테이블 컬럼:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # 3. 누락된 컬럼 확인 및 추가
            print("\n3. 누락된 컬럼 확인 및 추가...")
            expected_columns = {
                'author': 'VARCHAR(100)',
                'publisher': 'VARCHAR(100)',
                'isbn': 'VARCHAR(20)',
                'description': 'VARCHAR(500)',
                'publication_date': 'TIMESTAMP',
                'edition': 'VARCHAR(20)',
                'quantity': 'INTEGER',
                'min_quantity': 'INTEGER',
                'price': 'DOUBLE PRECISION',
                'expiry_date': 'TIMESTAMP',
                'is_active': 'BOOLEAN',
                'created_at': 'TIMESTAMP',
                'updated_at': 'TIMESTAMP'
            }
            
            existing_columns = [col[0] for col in columns]
            
            for col_name, col_type in expected_columns.items():
                if col_name not in existing_columns:
                    print(f"  추가 중: {col_name} {col_type}")
                    try:
                        session.execute(text(f"ALTER TABLE material ADD COLUMN {col_name} {col_type}"))
                        session.commit()
                        print(f"    ✅ {col_name} 컬럼 추가 완료")
                    except Exception as e:
                        print(f"    ❌ {col_name} 컬럼 추가 실패: {e}")
                        session.rollback()
                else:
                    print(f"  ✅ {col_name}: 이미 존재")
            
            # 4. 기본값 설정
            print("\n4. 기본값 설정...")
            try:
                session.execute(text("ALTER TABLE material ALTER COLUMN is_active SET DEFAULT true"))
                session.execute(text("ALTER TABLE material ALTER COLUMN quantity SET DEFAULT 0"))
                session.execute(text("ALTER TABLE material ALTER COLUMN min_quantity SET DEFAULT 5"))
                session.execute(text("ALTER TABLE material ALTER COLUMN price SET DEFAULT 0.0"))
                session.commit()
                print("  ✅ 기본값 설정 완료")
            except Exception as e:
                print(f"  ❌ 기본값 설정 실패: {e}")
                session.rollback()
            
            # 5. 최종 확인
            print("\n5. 최종 스키마 확인...")
            result = session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'material'
                ORDER BY ordinal_position;
            """))
            final_columns = result.fetchall()
            print("최종 material 테이블 컬럼:")
            for col in final_columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'}) [기본값: {col[3]}]")
            
            print("\n✅ PostgreSQL 스키마 확인 및 수정 완료!")
            
    except Exception as e:
        print(f"❌ 스키마 확인 중 오류: {e}")
        raise

if __name__ == "__main__":
    check_postgresql_schema() 
#!/usr/bin/env python3
"""
PostgreSQL 스키마 확인 스크립트
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_session
from sqlmodel import Session, text

def check_postgresql_schema():
    """PostgreSQL 스키마 확인"""
    print("=== PostgreSQL 스키마 확인 ===")
    
    try:
        with get_session() as session:
            # material 테이블 스키마 확인
            result = session.exec(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'material'
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 Material 테이블 컬럼:")
            for row in result:
                print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
            
            # lecture 테이블 스키마 확인
            result = session.exec(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'lecture'
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 Lecture 테이블 컬럼:")
            for row in result:
                print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
            
            # teacher 테이블 스키마 확인
            result = session.exec(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'teacher'
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 Teacher 테이블 컬럼:")
            for row in result:
                print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
            
            # student 테이블 스키마 확인
            result = session.exec(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'student'
                ORDER BY ordinal_position;
            """))
            
            print("\n📋 Student 테이블 컬럼:")
            for row in result:
                print(f"  - {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
                
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_postgresql_schema() 
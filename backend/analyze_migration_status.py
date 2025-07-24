#!/usr/bin/env python3
"""
PostgreSQL과 SQLite 데이터 비교 분석 스크립트
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlmodel import Session

# 현재 디렉터리를 파이썬 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'app'))

from app.core.config import get_settings

def analyze_migration_status():
    """PostgreSQL과 SQLite 데이터 비교 분석"""
    print("🔍 데이터 마이그레이션 상태 분석 시작...")
    
    settings = get_settings()
    
    # SQLite 연결
    sqlite_path = os.path.join(current_dir, "academy.db")
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite 파일을 찾을 수 없습니다: {sqlite_path}")
        return False
        
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    
    # PostgreSQL 연결
    if not settings.database_url or not settings.database_url.startswith("postgresql"):
        print("❌ PostgreSQL 연결 정보가 없습니다.")
        return False
    
    postgres_engine = create_engine(settings.database_url)
    
    print("\n📊 데이터 비교 분석:")
    print("=" * 60)
    
    # 테이블별 비교
    tables = ['student', 'teacher', 'material', 'lecture']
    
    for table in tables:
        print(f"\n📋 {table.upper()} 테이블:")
        print("-" * 40)
        
        # SQLite 데이터
        with Session(sqlite_engine) as session:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                sqlite_count = result.scalar()
                print(f"  SQLite: {sqlite_count}개")
                
                # 샘플 데이터 확인
                result = session.execute(text(f"SELECT * FROM {table} LIMIT 3"))
                sqlite_samples = result.fetchall()
                print(f"  SQLite 샘플: {len(sqlite_samples)}개 레코드")
                
            except Exception as e:
                print(f"  SQLite 오류: {e}")
                sqlite_count = 0
        
        # PostgreSQL 데이터
        with Session(postgres_engine) as session:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                postgres_count = result.scalar()
                print(f"  PostgreSQL: {postgres_count}개")
                
                # 샘플 데이터 확인
                result = session.execute(text(f"SELECT * FROM {table} LIMIT 3"))
                postgres_samples = result.fetchall()
                print(f"  PostgreSQL 샘플: {len(postgres_samples)}개 레코드")
                
                # 중복 확인 (email 기준)
                if table in ['student', 'teacher']:
                    result = session.execute(text(f"SELECT email, COUNT(*) FROM {table} GROUP BY email HAVING COUNT(*) > 1"))
                    duplicates = result.fetchall()
                    if duplicates:
                        print(f"  ⚠️ 중복 발견: {len(duplicates)}개 이메일 중복")
                    else:
                        print(f"  ✅ 중복 없음")
                
            except Exception as e:
                print(f"  PostgreSQL 오류: {e}")
                postgres_count = 0
        
        # 차이 분석
        if sqlite_count != postgres_count:
            diff = postgres_count - sqlite_count
            print(f"  🔍 차이: {diff:+d}개 ({'증가' if diff > 0 else '감소'})")
            if diff > 0:
                print(f"  ❌ 중복 마이그레이션 의심")
        else:
            print(f"  ✅ 데이터 일치")
    
    print("\n" + "=" * 60)
    print("📋 분석 완료!")
    
    return True

if __name__ == "__main__":
    analyze_migration_status() 
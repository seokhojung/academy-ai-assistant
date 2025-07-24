#!/usr/bin/env python3
"""
PostgreSQL 완전 초기화 후 정확한 마이그레이션 스크립트
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlmodel import Session

# 현재 디렉터리를 파이썬 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'app'))

from app.core.config import get_settings

def clean_migration():
    """PostgreSQL 완전 초기화 후 정확한 마이그레이션"""
    print("🧹 PostgreSQL 완전 초기화 및 정확한 마이그레이션 시작...")
    
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
    
    try:
        # 1. PostgreSQL 모든 테이블 완전 삭제
        print("🗑️ PostgreSQL 모든 테이블 완전 삭제...")
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
        
        # 2. 새로운 테이블 생성 (최신 스키마)
        print("🏗️ 새로운 테이블 생성 (최신 스키마)...")
        from app.core.database import create_db_and_tables
        create_db_and_tables()
        print("✅ 새 테이블 생성 완료!")
        
        # 3. academy.db에서 정확한 데이터 마이그레이션
        print("📊 academy.db에서 정확한 데이터 마이그레이션...")
        
        # 테이블 순서 (외래 키 의존성 고려)
        migration_order = ['student', 'teacher', 'material', 'lecture']
        
        for table in migration_order:
            print(f"  📋 {table} 테이블 마이그레이션...")
            
            with Session(sqlite_engine) as sqlite_session:
                # SQLite에서 데이터 읽기
                result = sqlite_session.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                
                if not rows:
                    print(f"    ⚠️ {table}: 데이터 없음")
                    continue
                
                # 컬럼 정보 가져오기
                result = sqlite_session.execute(text(f"PRAGMA table_info({table})"))
                columns = [row[1] for row in result.fetchall()]
                
                print(f"    📥 {len(rows)}개 레코드 읽기 완료")
                
                # PostgreSQL에 삽입
                with Session(postgres_engine) as postgres_session:
                    for row in rows:
                        try:
                            # 딕셔너리로 변환
                            row_dict = {}
                            for i, value in enumerate(row):
                                row_dict[columns[i]] = value
                            
                            # ID 제거 (자동 생성)
                            if 'id' in row_dict:
                                del row_dict['id']
                            
                            # 데이터 타입 변환
                            if 'is_active' in row_dict:
                                row_dict['is_active'] = bool(row_dict['is_active']) if row_dict['is_active'] is not None else True
                            
                            # SQL 쿼리 생성
                            cols = list(row_dict.keys())
                            placeholders = ', '.join([':' + col for col in cols])
                            column_names = ', '.join(cols)
                            
                            sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                            postgres_session.execute(text(sql), row_dict)
                            
                        except Exception as e:
                            print(f"    ❌ 레코드 삽입 실패: {e}")
                            postgres_session.rollback()
                            continue
                    
                    postgres_session.commit()
                    print(f"    ✅ {table} 테이블 마이그레이션 완료!")
        
        # 4. 결과 확인
        print("\n📊 마이그레이션 결과 확인:")
        print("=" * 50)
        
        with Session(postgres_engine) as session:
            for table in migration_order:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  {table}: {count}개")
                except Exception as e:
                    print(f"  {table}: 확인 실패 - {e}")
        
        print("\n🎉 PostgreSQL 완전 초기화 및 정확한 마이그레이션 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    clean_migration() 
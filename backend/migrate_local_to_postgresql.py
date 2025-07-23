#!/usr/bin/env python3
"""
로컬 SQLite 데이터를 PostgreSQL로 마이그레이션하는 스크립트
이 스크립트는 로컬 academy.db의 모든 데이터를 PostgreSQL로 정확히 복사합니다.
"""

import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sqlite3

# 환경 변수에서 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    print("Render 대시보드에서 DATABASE_URL을 확인하세요.")
    sys.exit(1)

def backup_sqlite_data():
    """SQLite 데이터를 JSON으로 백업"""
    try:
        print("📦 SQLite 데이터 백업 중...")
        
        # SQLite 연결
        sqlite_conn = sqlite3.connect('academy.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # 테이블 목록 가져오기
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        backup_data = {}
        
        for table in tables:
            print(f"  백업 중: {table}")
            
            # 테이블 스키마 가져오기
            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in sqlite_cursor.fetchall()]
            
            # 데이터 가져오기
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            # 딕셔너리로 변환
            table_data = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[columns[i]] = value
                table_data.append(row_dict)
            
            backup_data[table] = table_data
            print(f"    {len(table_data)}개 레코드 백업 완료")
        
        sqlite_conn.close()
        
        # JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"sqlite_backup_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 백업 완료: {backup_file}")
        return backup_data
        
    except Exception as e:
        print(f"❌ SQLite 백업 실패: {e}")
        return None

def migrate_to_postgresql(backup_data):
    """PostgreSQL로 데이터 마이그레이션"""
    try:
        print("\n🚀 PostgreSQL 마이그레이션 시작...")
        
        # PostgreSQL 엔진 생성
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # 기존 데이터 삭제 (테이블 순서 고려)
            print("\n1️⃣ 기존 데이터 삭제...")
            tables_to_clear = ['lecture', 'material', 'student', 'teacher', 'user', 'usercolumnsettings']
            
            for table in tables_to_clear:
                try:
                    session.execute(text(f"DELETE FROM {table}"))
                    print(f"  ✅ {table} 테이블 데이터 삭제")
                except Exception as e:
                    print(f"  ⚠️ {table} 테이블 삭제 실패: {e}")
            
            session.commit()
            
            # 새 데이터 삽입
            print("\n2️⃣ 새 데이터 삽입...")
            
            # 테이블별 데이터 삽입 (의존성 고려)
            insert_order = ['user', 'usercolumnsettings', 'student', 'teacher', 'material', 'lecture']
            
            for table in insert_order:
                if table in backup_data and backup_data[table]:
                    print(f"  삽입 중: {table} ({len(backup_data[table])}개)")
                    
                    for row_data in backup_data[table]:
                        try:
                            # ID 제거 (자동 생성)
                            if 'id' in row_data:
                                del row_data['id']
                            
                            # 컬럼명을 snake_case로 변환
                            columns = list(row_data.keys())
                            values = list(row_data.values())
                            
                            # SQL 쿼리 생성
                            placeholders = ', '.join([':' + col for col in columns])
                            column_names = ', '.join(columns)
                            
                            sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                            
                            session.execute(text(sql), row_data)
                            
                        except Exception as e:
                            print(f"    ❌ 레코드 삽입 실패: {e}")
                            print(f"    데이터: {row_data}")
                            session.rollback()
                            continue
                    
                    session.commit()
                    print(f"    ✅ {table} 테이블 삽입 완료")
            
            print("\n3️⃣ 마이그레이션 결과 확인...")
            
            # 결과 확인
            for table in ['student', 'teacher', 'material', 'lecture']:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  {table}: {count}개")
                except Exception as e:
                    print(f"  {table}: 확인 실패 - {e}")
            
            print("\n✅ PostgreSQL 마이그레이션 완료!")
            return True
            
    except Exception as e:
        print(f"❌ PostgreSQL 마이그레이션 실패: {e}")
        return False

def verify_migration():
    """마이그레이션 결과 검증"""
    try:
        print("\n🔍 마이그레이션 결과 검증...")
        
        engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # 각 테이블의 데이터 수 확인
            for table in ['student', 'teacher', 'material', 'lecture']:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  {table}: {count}개")
                    
                    # 샘플 데이터 출력
                    if count > 0:
                        result = session.execute(text(f"SELECT * FROM {table} LIMIT 2"))
                        rows = result.fetchall()
                        for i, row in enumerate(rows, 1):
                            print(f"    {i}. {row}")
                except Exception as e:
                    print(f"  {table}: 검증 실패 - {e}")
        
        print("\n✅ 검증 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 검증 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 로컬 SQLite → PostgreSQL 마이그레이션 시작")
    print("=" * 60)
    
    # 1. SQLite 데이터 백업
    backup_data = backup_sqlite_data()
    
    if not backup_data:
        print("❌ 백업 실패로 마이그레이션을 중단합니다.")
        sys.exit(1)
    
    # 2. PostgreSQL로 마이그레이션
    success = migrate_to_postgresql(backup_data)
    
    if success:
        # 3. 결과 검증
        verify_migration()
        
        print("\n" + "=" * 60)
        print("🎉 마이그레이션 완료!")
        print("이제 웹 AI 챗봇이 로컬과 동일한 데이터를 표시할 것입니다.")
        print("=" * 60)
    else:
        print("\n❌ 마이그레이션에 실패했습니다.")
        print("Render 로그를 확인하여 오류를 확인하세요.") 
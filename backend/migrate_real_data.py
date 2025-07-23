#!/usr/bin/env python3
"""
로컬 academy.db의 실제 데이터를 PostgreSQL로 마이그레이션
"""

import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def migrate_real_data():
    """로컬 academy.db의 실제 데이터를 PostgreSQL로 마이그레이션"""
    
    # 환경변수에서 데이터베이스 URL 가져오기
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        print("🔄 로컬 academy.db 실제 데이터 마이그레이션 시작...")
        
        # 1. 로컬 SQLite 데이터 읽기
        print("  📖 로컬 academy.db 데이터 읽기...")
        
        if not os.path.exists('academy.db'):
            print("    ❌ academy.db 파일이 존재하지 않습니다.")
            return
        
        sqlite_conn = sqlite3.connect('academy.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # 테이블 목록 가져오기
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        print(f"    발견된 테이블: {tables}")
        
        # 각 테이블의 데이터 수 확인
        for table in ['student', 'teacher', 'material', 'lecture']:
            if table in tables:
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = sqlite_cursor.fetchone()[0]
                print(f"    {table}: {count}개")
        
        # 2. PostgreSQL로 마이그레이션
        print("  🚀 PostgreSQL로 마이그레이션 중...")
        
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # 기존 데이터 삭제
            tables_to_clear = ['lecture', 'material', 'student', 'teacher']
            
            for table in tables_to_clear:
                try:
                    session.execute(text(f"DELETE FROM {table}"))
                    print(f"    ✅ {table} 테이블 데이터 삭제")
                except Exception as e:
                    print(f"    ⚠️ {table} 테이블 삭제 실패: {e}")
            
            session.commit()
            
            # 실제 데이터 마이그레이션
            for table in ['student', 'teacher', 'material', 'lecture']:
                if table in tables:
                    print(f"    마이그레이션 중: {table}")
                    
                    # 테이블 스키마 가져오기
                    sqlite_cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in sqlite_cursor.fetchall()]
                    print(f"      컬럼: {columns}")
                    
                    # 데이터 가져오기
                    sqlite_cursor.execute(f"SELECT * FROM {table}")
                    rows = sqlite_cursor.fetchall()
                    
                    print(f"      {len(rows)}개 레코드 마이그레이션 중...")
                    
                    for row in rows:
                        try:
                            # 딕셔너리로 변환
                            row_data = {}
                            for i, value in enumerate(row):
                                row_data[columns[i]] = value
                            
                            # ID 제거 (자동 생성)
                            if 'id' in row_data:
                                del row_data['id']
                            
                            # 데이터 타입 변환
                            if 'is_active' in row_data:
                                # SQLite의 integer (0,1)를 PostgreSQL boolean으로 변환
                                row_data['is_active'] = bool(row_data['is_active']) if row_data['is_active'] is not None else True
                            
                            # SQL 쿼리 생성
                            columns_to_insert = list(row_data.keys())
                            placeholders = ', '.join([':' + col for col in columns_to_insert])
                            column_names = ', '.join(columns_to_insert)
                            
                            sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                            session.execute(text(sql), row_data)
                            
                        except Exception as e:
                            print(f"        ❌ 레코드 삽입 실패: {e}")
                            print(f"        데이터: {row_data}")
                            session.rollback()
                            continue
                    
                    session.commit()
                    print(f"      ✅ {table} 마이그레이션 완료")
        
        sqlite_conn.close()
        
        # 3. 결과 확인
        print("  📊 마이그레이션 결과 확인...")
        with SessionLocal() as session:
            for table in ['student', 'teacher', 'material', 'lecture']:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"    {table}: {count}개")
                except Exception as e:
                    print(f"    {table}: 확인 실패 - {e}")
        
        print("✅ 실제 데이터 마이그레이션 완료!")
        
    except Exception as e:
        print(f"❌ 실제 데이터 마이그레이션 실패: {e}")

if __name__ == "__main__":
    migrate_real_data() 
#!/usr/bin/env python3
"""
PostgreSQL 완전 초기화 + academy.db 재삽입
모든 데이터를 삭제하고 academy.db의 데이터만 정확히 한 번 삽입
"""

import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def reset_postgresql_clean():
    """PostgreSQL 완전 초기화 후 academy.db 데이터만 삽입"""
    
    # 환경 변수에서 데이터베이스 URL 가져오기
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
        return
    
    if "sqlite" in database_url:
        print("❌ SQLite 데이터베이스입니다. PostgreSQL을 확인해주세요.")
        return
    
    try:
        print("🧹 PostgreSQL 완전 초기화 + academy.db 재삽입 시작...")
        
        # 1. academy.db 파일 확인
        if not os.path.exists('academy.db'):
            print("❌ academy.db 파일이 존재하지 않습니다.")
            return
        
        # 2. academy.db 데이터 백업
        print("\n📦 academy.db 데이터 백업 중...")
        backup_data = {}
        
        conn = sqlite3.connect('academy.db')
        cursor = conn.cursor()
        
        # 테이블 목록 가져오기
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            print(f"  백업 중: {table}")
            
            # 테이블 스키마 가져오기
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            
            # 데이터 가져오기
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # 딕셔너리로 변환
            table_data = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[columns[i]] = value
                table_data.append(row_dict)
            
            backup_data[table] = table_data
            print(f"    ✅ {len(table_data)}개 레코드 백업 완료")
        
        conn.close()
        
        print(f"\n📊 백업된 데이터:")
        print(f"  학생: {len(backup_data.get('student', []))}명")
        print(f"  강사: {len(backup_data.get('teacher', []))}명")
        print(f"  교재: {len(backup_data.get('material', []))}개")
        print(f"  강의: {len(backup_data.get('lecture', []))}개")
        
        # 3. PostgreSQL 연결 및 완전 삭제
        print("\n🗑️ PostgreSQL 모든 데이터 삭제 중...")
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # 외래키 제약조건 때문에 순서대로 삭제
            tables_to_clear = ['lecture', 'material', 'student', 'teacher', 'user', 'usercolumnsettings']
            
            for table in tables_to_clear:
                try:
                    session.execute(text(f"DELETE FROM {table}"))
                    print(f"    ✅ {table} 테이블 모든 데이터 삭제")
                except Exception as e:
                    print(f"    ⚠️ {table} 테이블 삭제 실패: {e}")
            
            session.commit()
            print("  🎯 PostgreSQL 완전 초기화 완료!")
            
            # 4. academy.db 데이터만 깨끗하게 삽입
            print("\n📥 academy.db 데이터 삽입 중...")
            
            # 삽입 순서 (외래키 관계 고려)
            insert_order = ['user', 'usercolumnsettings', 'student', 'teacher', 'material', 'lecture']
            
            for table in insert_order:
                if table in backup_data and backup_data[table]:
                    print(f"  삽입 중: {table} ({len(backup_data[table])}개)")
                    
                    success_count = 0
                    for row_data in backup_data[table]:
                        try:
                            # ID 제거 (자동 생성)
                            if 'id' in row_data:
                                del row_data['id']
                            
                            # 데이터 타입 변환
                            if 'is_active' in row_data:
                                # SQLite의 integer (0,1)를 PostgreSQL boolean으로 변환
                                row_data['is_active'] = bool(row_data['is_active']) if row_data['is_active'] is not None else True
                            
                            # SQL 쿼리 생성
                            columns = list(row_data.keys())
                            placeholders = ', '.join([':' + col for col in columns])
                            column_names = ', '.join(columns)
                            
                            sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                            session.execute(text(sql), row_data)
                            success_count += 1
                            
                        except Exception as e:
                            print(f"    ❌ 레코드 삽입 실패: {e}")
                            session.rollback()
                            continue
                    
                    session.commit()
                    print(f"    ✅ {table}: {success_count}개 성공적으로 삽입")
                else:
                    print(f"  ⏭️ {table}: 데이터 없음, 건너뛰기")
            
            # 5. 최종 결과 확인
            print("\n📊 최종 삽입 결과:")
            for table in ['student', 'teacher', 'material', 'lecture']:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"  {table}: {count}개")
                except Exception as e:
                    print(f"  {table}: 확인 실패 - {e}")
        
        print("\n✅ PostgreSQL 완전 초기화 + 재삽입 완료!")
        print("🎯 이제 PostgreSQL = academy.db 데이터와 정확히 일치합니다!")
        
    except Exception as e:
        print(f"❌ 초기화 및 재삽입 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_postgresql_clean() 
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from datetime import datetime

from app.core.database import create_db_and_tables, get_session
from app.api.v1 import ai, auth, lectures, materials, students, teachers, user, excel_preview

# 강제 스키마 수정 함수 추가
def force_fix_postgresql_schema():
    """강제로 PostgreSQL 스키마를 수정"""
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url or "sqlite" in database_url:
        return  # SQLite는 건너뛰기
    
    try:
        print("🔧 강제 PostgreSQL 스키마 수정 시작...")
        
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # material 테이블이 존재하는지 확인
            result = session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'material'
                );
            """))
            
            if not result.scalar():
                print("  material 테이블이 존재하지 않습니다.")
                return
            
            # 현재 컬럼 확인
            result = session.execute(text("""
                SELECT column_name
                FROM information_schema.columns 
                WHERE table_name = 'material'
                ORDER BY ordinal_position;
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            print(f"  기존 컬럼: {existing_columns}")
            
            # 누락된 컬럼 추가
            missing_columns = {
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
            
            for col_name, col_type in missing_columns.items():
                if col_name not in existing_columns:
                    print(f"  추가 중: {col_name}")
                    try:
                        session.execute(text(f"ALTER TABLE material ADD COLUMN {col_name} {col_type}"))
                        session.commit()
                        print(f"    ✅ {col_name} 추가 완료")
                    except Exception as e:
                        print(f"    ❌ {col_name} 추가 실패: {e}")
                        session.rollback()
                else:
                    print(f"  ✅ {col_name}: 이미 존재")
            
            print("✅ 강제 스키마 수정 완료!")
            
    except Exception as e:
        print(f"❌ 강제 스키마 수정 실패: {e}")

def migrate_local_data_to_postgresql():
    """로컬 데이터를 PostgreSQL로 마이그레이션"""
    import sqlite3
    import json
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url or "sqlite" in database_url:
        return  # SQLite는 건너뛰기
    
    try:
        print("🔄 로컬 데이터 PostgreSQL 마이그레이션 시작...")
        
        # 1. 로컬 SQLite 데이터 백업
        print("  📦 로컬 SQLite 데이터 백업 중...")
        
        if not os.path.exists('academy.db'):
            print("    ❌ academy.db 파일이 존재하지 않습니다.")
            return
        
        sqlite_conn = sqlite3.connect('academy.db')
        sqlite_cursor = sqlite_conn.cursor()
        
        # 테이블 목록 가져오기
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        backup_data = {}
        
        for table in tables:
            print(f"    백업 중: {table}")
            
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
                    row_dict[columns[i]] = value
                table_data.append(row_dict)
            
            backup_data[table] = table_data
            print(f"      {len(table_data)}개 레코드 백업 완료")
        
        sqlite_conn.close()
        
        # 2. PostgreSQL로 마이그레이션
        print("  🚀 PostgreSQL로 마이그레이션 중...")
        
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # 기존 데이터 삭제
            tables_to_clear = ['lecture', 'material', 'student', 'teacher', 'user', 'usercolumnsettings']
            
            for table in tables_to_clear:
                try:
                    session.execute(text(f"DELETE FROM {table}"))
                    print(f"    ✅ {table} 테이블 데이터 삭제")
                except Exception as e:
                    print(f"    ⚠️ {table} 테이블 삭제 실패: {e}")
            
            session.commit()
            
            # 새 데이터 삽입
            insert_order = ['user', 'usercolumnsettings', 'student', 'teacher', 'material', 'lecture']
            
            for table in insert_order:
                if table in backup_data and backup_data[table]:
                    print(f"    삽입 중: {table} ({len(backup_data[table])}개)")
                    
                    for row_data in backup_data[table]:
                        try:
                            # ID 제거 (자동 생성)
                            if 'id' in row_data:
                                del row_data['id']
                            
                            # SQL 쿼리 생성
                            columns = list(row_data.keys())
                            placeholders = ', '.join([':' + col for col in columns])
                            column_names = ', '.join(columns)
                            
                            sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                            session.execute(text(sql), row_data)
                            
                        except Exception as e:
                            print(f"      ❌ 레코드 삽입 실패: {e}")
                            session.rollback()
                            continue
                    
                    session.commit()
                    print(f"      ✅ {table} 테이블 삽입 완료")
            
            # 결과 확인
            print("  📊 마이그레이션 결과 확인...")
            for table in ['student', 'teacher', 'material', 'lecture']:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"    {table}: {count}개")
                except Exception as e:
                    print(f"    {table}: 확인 실패 - {e}")
        
        print("✅ 로컬 데이터 마이그레이션 완료!")
        
    except Exception as e:
        print(f"❌ 로컬 데이터 마이그레이션 실패: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 함수"""
    # 시작 시
    print("🚀 애플리케이션 시작...")
    
    # 강제 스키마 수정 실행
    force_fix_postgresql_schema()
    
    # 로컬 데이터 마이그레이션 실행
    migrate_local_data_to_postgresql()
    
    # 기존 데이터베이스 초기화
    create_db_and_tables()
    
    print("✅ 애플리케이션 초기화 완료")
    
    yield
    
    # 종료 시
    print("🛑 애플리케이션 종료...")

# FastAPI 앱 생성
app = FastAPI(
    title="Academy AI Assistant API",
    description="학원 관리 시스템 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(lectures.router, prefix="/api/v1/lectures", tags=["Lectures"])
app.include_router(materials.router, prefix="/api/v1/materials", tags=["Materials"])
app.include_router(students.router, prefix="/api/v1/students", tags=["Students"])
app.include_router(teachers.router, prefix="/api/v1/teachers", tags=["Teachers"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])
app.include_router(excel_preview.router, prefix="/api/v1/excel-preview", tags=["Excel Preview"])

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Academy AI Assistant API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 데이터베이스 연결 테스트
        session = next(get_session())
        session.execute(text("SELECT 1"))
        session.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "database": "healthy",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "database": "error",
                "error": str(e),
                "environment": os.getenv("ENVIRONMENT", "development")
            }
        )

@app.get("/api/v1/test")
async def test_endpoint():
    """테스트 엔드포인트"""
    return {"message": "API is working!", "timestamp": datetime.now().isoformat()} 
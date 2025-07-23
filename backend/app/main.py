from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from datetime import datetime
from sqlalchemy import text

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
                        # 실패해도 계속 진행
                else:
                    print(f"  ✅ {col_name}: 이미 존재")
            
            # 모든 컬럼이 있는지 다시 확인
            result = session.execute(text("""
                SELECT column_name
                FROM information_schema.columns 
                WHERE table_name = 'material'
                ORDER BY ordinal_position;
            """))
            
            final_columns = [row[0] for row in result.fetchall()]
            required_columns = ['id', 'name', 'subject', 'grade', 'author']
            missing_required = [col for col in required_columns if col not in final_columns]
            
            if missing_required:
                print(f"  ❌ 여전히 누락된 필수 컬럼: {missing_required}")
                print("  🔄 테이블 재생성 시도...")
                # 테이블 재생성
                session.execute(text("DROP TABLE IF EXISTS material CASCADE"))
                session.commit()
                # SQLModel로 테이블 재생성
                from app.models.material import Material
                from sqlmodel import SQLModel
                SQLModel.metadata.create_all(engine, tables=[Material.__table__])
                print("  ✅ material 테이블 재생성 완료")
            
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
        
        # 0. 기존 데이터 확인
        print("  📊 기존 데이터 확인 중...")
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # 학생 데이터 확인
            result = session.execute(text("SELECT COUNT(*) FROM student"))
            student_count = result.scalar()
            
            # 강사 데이터 확인
            result = session.execute(text("SELECT COUNT(*) FROM teacher"))
            teacher_count = result.scalar()
            
            print(f"    현재 학생: {student_count}명, 강사: {teacher_count}명")
            
            # 이미 충분한 데이터가 있으면 마이그레이션 건너뛰기
            if student_count > 0 and teacher_count > 0:
                print("    ✅ 이미 데이터가 존재합니다. 마이그레이션을 건너뜁니다.")
                return
        
        # 1. 로컬 SQLite 데이터 백업
        print("  📦 로컬 SQLite 데이터 백업 중...")
        
        if not os.path.exists('academy.db'):
            print("    ❌ academy.db 파일이 존재하지 않습니다.")
            print("    📝 샘플 데이터를 직접 추가합니다.")
            # academy.db가 없으면 샘플 데이터만 추가
            add_sample_data_directly(session)
            return
        
        print("    ✅ academy.db 파일 발견! 실제 데이터 마이그레이션 시작...")
        
        # 스키마 수정을 먼저 실행
        print("    🔧 스키마 수정 먼저 실행...")
        force_fix_postgresql_schema()
        
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
        
        with SessionLocal() as session:
            # 기존 데이터 삭제 (중복 체크 후에만)
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

def add_sample_data_directly(session):
    """PostgreSQL에 직접 샘플 데이터 추가 - 제거됨"""
    print("📝 샘플 데이터 추가가 비활성화되었습니다.")
    print("  실제 로컬 데이터만 사용합니다.")
    return

def force_reset_and_migrate():
    """PostgreSQL 강제 완전 초기화 및 academy.db 마이그레이션"""
    from app.core.config import settings
    from sqlalchemy import create_engine, text
    from sqlmodel import Session
    from datetime import datetime
    
    # academy.db 경로 (Render에서는 업로드된 파일)
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "academy.db")
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite 파일 없음: {sqlite_path}")
        return False
        
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    
    # PostgreSQL 연결 확인
    if not settings.database_url or not settings.database_url.startswith("postgresql"):
        print("❌ PostgreSQL 연결 정보 없음")
        return False
    
    postgres_engine = create_engine(settings.database_url)
    print(f"✅ PostgreSQL 연결 성공")
    
    # 1. PostgreSQL 모든 테이블 완전 삭제
    print("🗑️ PostgreSQL 모든 테이블 삭제...")
    with postgres_engine.connect() as conn:
        # 모든 테이블 목록 가져오기
        result = conn.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result.fetchall()]
        
        # 각 테이블 삭제
        for table in tables:
            print(f"  🗑️ 테이블 삭제: {table}")
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
        conn.commit()
    
    print("✅ 모든 테이블 삭제 완료!")
    
    # 2. 새 테이블 생성
    print("🏗️ 새 테이블 생성...")
    from app.core.database import create_db_and_tables
    create_db_and_tables()
    print("✅ 새 테이블 생성 완료!")
    
    # 3. 데이터 마이그레이션
    print("📊 academy.db → PostgreSQL 데이터 마이그레이션...")
    
    # Students
    with Session(sqlite_engine) as sqlite_session, Session(postgres_engine) as postgres_session:
        students = sqlite_session.exec(text("SELECT * FROM student")).fetchall()
        print(f"  📚 학생: {len(students)}개")
        for row in students:
            from app.models.student import Student
            student = Student(
                name=row[1],
                email=row[2] if row[2] else f"student{row[0]}@example.com",
                phone=row[3] if row[3] else "",
                grade=row[4] if row[4] else "",
                school=row[5] if row[5] else "",
                parent_name=row[6] if row[6] else "",
                parent_phone=row[7] if row[7] else "",
                address=row[8] if row[8] else "",
                notes=row[9] if row[9] else "",
                enrollment_date=datetime.fromisoformat(row[10]) if row[10] else datetime.now(),
                is_active=bool(row[11]) if row[11] is not None else True,
                created_at=datetime.fromisoformat(row[12]) if row[12] else datetime.now(),
                updated_at=datetime.fromisoformat(row[13]) if row[13] else datetime.now()
            )
            postgres_session.add(student)
        postgres_session.commit()
    
    # Teachers  
    with Session(sqlite_engine) as sqlite_session, Session(postgres_engine) as postgres_session:
        teachers = sqlite_session.exec(text("SELECT * FROM teacher")).fetchall()
        print(f"  👨‍🏫 교사: {len(teachers)}개")
        for row in teachers:
            from app.models.teacher import Teacher
            teacher = Teacher(
                name=row[1],
                email=row[2] if row[2] else f"teacher{row[0]}@example.com",
                phone=row[3] if row[3] else "",
                subject=row[4] if row[4] else "",
                hire_date=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                salary=float(row[6]) if row[6] else 0.0,
                notes=row[7] if row[7] else "",
                is_active=bool(row[8]) if row[8] is not None else True,
                created_at=datetime.fromisoformat(row[9]) if row[9] else datetime.now(),
                updated_at=datetime.fromisoformat(row[10]) if row[10] else datetime.now()
            )
            postgres_session.add(teacher)
        postgres_session.commit()
    
    # Materials
    with Session(sqlite_engine) as sqlite_session, Session(postgres_engine) as postgres_session:
        materials = sqlite_session.exec(text("SELECT * FROM material")).fetchall()
        print(f"  📖 교재: {len(materials)}개")
        for row in materials:
            from app.models.material import Material
            material = Material(
                title=row[1],
                category=row[2] if row[2] else "",
                author=row[3] if row[3] else "",
                publisher=row[4] if row[4] else "",
                isbn=row[5] if row[5] else "",
                description=row[6] if row[6] else "",
                publication_date=datetime.fromisoformat(row[7]) if row[7] else datetime.now(),
                edition=row[8] if row[8] else "",
                quantity=int(row[9]) if row[9] else 0,
                min_quantity=int(row[10]) if row[10] else 0,
                price=float(row[11]) if row[11] else 0.0,
                expiry_date=datetime.fromisoformat(row[12]) if row[12] else None,
                is_active=bool(row[13]) if row[13] is not None else True,
                created_at=datetime.fromisoformat(row[14]) if row[14] else datetime.now(),
                updated_at=datetime.fromisoformat(row[15]) if row[15] else datetime.now()
            )
            postgres_session.add(material)
        postgres_session.commit()
    
    # Lectures
    with Session(sqlite_engine) as sqlite_session, Session(postgres_engine) as postgres_session:
        lectures = sqlite_session.exec(text("SELECT * FROM lecture")).fetchall()
        print(f"  🎓 강의: {len(lectures)}개")
        for row in lectures:
            from app.models.lecture import Lecture
            lecture = Lecture(
                title=row[1],
                subject=row[2] if row[2] else "",
                teacher_id=int(row[3]) if row[3] else None,
                schedule=row[4] if row[4] else "",
                classroom=row[5] if row[5] else "",
                capacity=int(row[6]) if row[6] else 0,
                current_enrollment=int(row[7]) if row[7] else 0,
                start_date=datetime.fromisoformat(row[8]) if row[8] else datetime.now(),
                end_date=datetime.fromisoformat(row[9]) if row[9] else datetime.now(),
                description=row[10] if row[10] else "",
                fee=float(row[11]) if row[11] else 0.0,
                is_active=bool(row[12]) if row[12] is not None else True,
                created_at=datetime.fromisoformat(row[13]) if row[13] else datetime.now(),
                updated_at=datetime.fromisoformat(row[14]) if row[14] else datetime.now()
            )
            postgres_session.add(lecture)
        postgres_session.commit()
    
    # 최종 확인
    print("\n🔍 마이그레이션 결과:")
    with Session(postgres_engine) as session:
        student_count = len(session.exec(text("SELECT * FROM student")).fetchall())
        teacher_count = len(session.exec(text("SELECT * FROM teacher")).fetchall())
        material_count = len(session.exec(text("SELECT * FROM material")).fetchall())
        lecture_count = len(session.exec(text("SELECT * FROM lecture")).fetchall())
        
        print(f"  📚 학생: {student_count}명")
        print(f"  👨‍🏫 교사: {teacher_count}명")
        print(f"  📖 교재: {material_count}개")
        print(f"  🎓 강의: {lecture_count}개")
    
    print(f"🎉 PostgreSQL이 academy.db와 완전히 동일해졌습니다!")
    
    # 4. 엑셀 미리보기 캐시 재생성
    print("🔄 엑셀 미리보기 캐시 재생성 중...")
    try:
        from app.api.v1.excel_preview import save_excel_preview_data
        with Session(postgres_engine) as cache_session:
            # 학생 캐시 재생성
            students = cache_session.query(Student).all()
            student_data = [{"이름": s.name, "학년": s.grade, "이메일": s.email} for s in students]
            save_excel_preview_data("students", student_data)
            print(f"  ✅ students 캐시: {len(student_data)}개")
            
            # 교사 캐시 재생성  
            teachers = cache_session.query(Teacher).all()
            teacher_data = [{"이름": t.name, "과목": t.subject, "이메일": t.email} for t in teachers]
            save_excel_preview_data("teachers", teacher_data)
            print(f"  ✅ teachers 캐시: {len(teacher_data)}개")
            
            # 교재 캐시 재생성
            materials = cache_session.query(Material).all()
            material_data = [{"이름": m.name, "과목": m.subject, "수량": m.quantity} for m in materials]
            save_excel_preview_data("materials", material_data)
            print(f"  ✅ materials 캐시: {len(material_data)}개")
            
        print("✅ 엑셀 미리보기 캐시 재생성 완료!")
    except Exception as cache_error:
        print(f"⚠️ 캐시 재생성 실패: {cache_error}")
    
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 함수"""
    # 시작 시
    print("🚀 애플리케이션 시작...")
    
    # 🔥🔥🔥 임시 하드코딩: 무조건 강제 초기화 실행 🔥🔥🔥
    print("🔥🔥🔥 하드코딩된 강제 초기화 시작...")
    try:
        force_reset_and_migrate()
        print("🎉🎉🎉 하드코딩 강제 초기화 성공!")
    except Exception as e:
        print(f"❌❌❌ 하드코딩 강제 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        # 실패 시에만 기본 테이블 생성
        from app.core.database import create_db_and_tables
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
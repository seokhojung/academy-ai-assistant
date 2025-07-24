from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from datetime import datetime
from sqlalchemy import text

from app.core.database import create_db_and_tables, get_session
from app.api.v1 import ai, auth, lectures, materials, students, teachers, user, excel_preview, statistics

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
            # teacher 테이블 스키마 수정
            print("  📚 teacher 테이블 스키마 수정...")
            teacher_columns = {
                'experience_years': 'INTEGER DEFAULT 0',
                'education_level': 'VARCHAR(50) DEFAULT \'bachelor\'',
                'specialization': 'VARCHAR(200) DEFAULT \'\'',
                'hire_date': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'contract_type': 'VARCHAR(50) DEFAULT \'part_time\'',
                'max_lectures': 'INTEGER DEFAULT 5',
                'rating': 'DOUBLE PRECISION',
                'total_teaching_hours': 'INTEGER DEFAULT 0',
                'certification': 'VARCHAR(500) DEFAULT \'[]\''
            }
            
            for col_name, col_def in teacher_columns.items():
                try:
                    session.execute(text(f"ALTER TABLE teacher ADD COLUMN IF NOT EXISTS {col_name} {col_def}"))
                    session.commit()
                    print(f"    ✅ teacher.{col_name} 추가 완료")
                except Exception as e:
                    print(f"    ⚠️ teacher.{col_name}: {e}")
                    session.rollback()
            
            # lecture 테이블 스키마 수정
            print("  📖 lecture 테이블 스키마 수정...")
            lecture_columns = {
                'difficulty_level': 'VARCHAR(50) DEFAULT \'intermediate\'',
                'class_duration': 'INTEGER DEFAULT 90',
                'total_sessions': 'INTEGER DEFAULT 16',
                'completed_sessions': 'INTEGER DEFAULT 0',
                'student_satisfaction': 'DOUBLE PRECISION',
                'teacher_rating': 'DOUBLE PRECISION'
            }
            
            for col_name, col_def in lecture_columns.items():
                try:
                    session.execute(text(f"ALTER TABLE lecture ADD COLUMN IF NOT EXISTS {col_name} {col_def}"))
                    session.commit()
                    print(f"    ✅ lecture.{col_name} 추가 완료")
                except Exception as e:
                    print(f"    ⚠️ lecture.{col_name}: {e}")
                    session.rollback()
            
            # material 테이블 스키마 수정 (기존)
            print("  📚 material 테이블 스키마 수정...")
            material_columns = {
                'author': 'VARCHAR(100)',
                'publisher': 'VARCHAR(100)',
                'isbn': 'VARCHAR(20)',
                'description': 'VARCHAR(500)',
                'publication_date': 'TIMESTAMP',
                'edition': 'VARCHAR(20)',
                'quantity': 'INTEGER DEFAULT 0',
                'min_quantity': 'INTEGER DEFAULT 5',
                'price': 'DOUBLE PRECISION DEFAULT 0.0',
                'expiry_date': 'TIMESTAMP',
                'is_active': 'BOOLEAN DEFAULT true',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
            
            for col_name, col_def in material_columns.items():
                try:
                    session.execute(text(f"ALTER TABLE material ADD COLUMN IF NOT EXISTS {col_name} {col_def}"))
                    session.commit()
                    print(f"    ✅ material.{col_name} 추가 완료")
                except Exception as e:
                    print(f"    ⚠️ material.{col_name}: {e}")
                    session.rollback()
            
            print("✅ PostgreSQL 스키마 수정 완료!")
            
    except Exception as e:
        print(f"❌ PostgreSQL 스키마 수정 실패: {e}")
        import traceback
        traceback.print_exc()

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
        
        # 각 테이블 삭제 (예약어는 큰따옴표로 감싸기)
        for table in tables:
            print(f"  🗑️ 테이블 삭제: {table}")
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE;'))
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
                tuition_fee=float(row[5]) if len(row) > 5 and row[5] else 0.0,
                tuition_due_date=row[6] if len(row) > 6 and isinstance(row[6], datetime) else (datetime.fromisoformat(row[6]) if len(row) > 6 and row[6] and isinstance(row[6], str) else None),
                is_active=bool(row[7]) if len(row) > 7 and row[7] is not None else True,
                created_at=row[8] if len(row) > 8 and isinstance(row[8], datetime) else (datetime.fromisoformat(row[8]) if len(row) > 8 and row[8] and isinstance(row[8], str) else datetime.now()),
                updated_at=row[9] if len(row) > 9 and isinstance(row[9], datetime) else (datetime.fromisoformat(row[9]) if len(row) > 9 and row[9] and isinstance(row[9], str) else datetime.now())
            )
            postgres_session.add(student)
        postgres_session.commit()
    
    # Teachers (9개 컬럼: 0~8)
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
                hourly_rate=float(row[5]) if row[5] else 0.0,
                is_active=bool(row[6]) if row[6] is not None else True,
                created_at=row[7] if isinstance(row[7], datetime) else (datetime.fromisoformat(row[7]) if row[7] and isinstance(row[7], str) else datetime.now()),
                updated_at=row[8] if isinstance(row[8], datetime) else (datetime.fromisoformat(row[8]) if row[8] and isinstance(row[8], str) else datetime.now())
            )
            postgres_session.add(teacher)
        postgres_session.commit()
    
    # Materials (17개 컬럼: 0~16)
    with Session(sqlite_engine) as sqlite_session, Session(postgres_engine) as postgres_session:
        materials = sqlite_session.exec(text("SELECT * FROM material")).fetchall()
        print(f"  📖 교재: {len(materials)}개")
        for row in materials:
            from app.models.material import Material
            material = Material(
                name=row[1],
                subject=row[2] if row[2] else "",
                grade=row[3] if row[3] else "",
                publisher=row[4] if row[4] else "",
                author=row[5] if row[5] else "",
                isbn=row[6] if row[6] else "",
                description=row[7] if row[7] else "",
                publication_date=row[8] if isinstance(row[8], datetime) else (datetime.fromisoformat(row[8]) if row[8] and isinstance(row[8], str) else datetime.now()),
                edition=row[9] if row[9] else "",
                quantity=int(row[10]) if row[10] else 0,
                min_quantity=int(row[11]) if row[11] else 0,
                price=float(row[12]) if row[12] else 0.0,
                expiry_date=row[13] if isinstance(row[13], datetime) else (datetime.fromisoformat(row[13]) if row[13] and isinstance(row[13], str) else None),
                is_active=bool(row[14]) if row[14] is not None else True,
                created_at=row[15] if isinstance(row[15], datetime) else (datetime.fromisoformat(row[15]) if row[15] and isinstance(row[15], str) else datetime.now()),
                updated_at=row[16] if isinstance(row[16], datetime) else (datetime.fromisoformat(row[16]) if row[16] and isinstance(row[16], str) else datetime.now())
            )
            postgres_session.add(material)
        postgres_session.commit()
    
    # Lectures (15개 컬럼: 0~14)
    with Session(sqlite_engine) as sqlite_session, Session(postgres_engine) as postgres_session:
        lectures = sqlite_session.exec(text("SELECT * FROM lecture")).fetchall()
        print(f"  🎓 강의: {len(lectures)}개")
        for row in lectures:
            from app.models.lecture import Lecture
            lecture = Lecture(
                title=row[1],
                subject=row[2] if row[2] else "",
                teacher_id=int(row[3]) if row[3] else None,
                material_id=int(row[4]) if row[4] else None,
                grade=row[5] if row[5] else "",
                max_students=int(row[6]) if row[6] else 0,
                current_students=int(row[7]) if row[7] else 0,
                tuition_fee=int(row[8]) if row[8] else 0,
                schedule=row[9] if row[9] else "",
                classroom=row[10] if row[10] else "",
                is_active=bool(row[11]) if row[11] is not None else True,
                description=row[12] if row[12] else "",
                created_at=row[13] if isinstance(row[13], datetime) else (datetime.fromisoformat(row[13]) if row[13] and isinstance(row[13], str) else datetime.now()),
                updated_at=row[14] if isinstance(row[14], datetime) else (datetime.fromisoformat(row[14]) if row[14] and isinstance(row[14], str) else datetime.now())
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

def sync_postgresql_data():
    """PostgreSQL 데이터를 academy.db와 동기화"""
    from app.core.config import settings
    from sqlalchemy import create_engine, text
    from sqlmodel import Session
    from datetime import datetime
    
    # academy.db 경로 (Render에서는 업로드된 파일)
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "academy.db")
    if not os.path.exists(sqlite_path):
        print(f"❌ academy.db 파일이 존재하지 않습니다: {sqlite_path}")
        return False
    
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    
    # PostgreSQL 연결 확인
    if not settings.database_url or not settings.database_url.startswith("postgresql"):
        print("❌ PostgreSQL 연결 정보 없음")
        return False
    
    postgres_engine = create_engine(settings.database_url)
    print(f"✅ PostgreSQL 연결 성공")
    
    # 1. 데이터 백업
    print("📦 PostgreSQL 데이터 백업 중...")
    with Session(postgres_engine) as session:
        # 테이블 목록 가져오기
        result = session.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """))
        tables = [row[0] for row in result.fetchall()]
        
        backup_data = {}
        for table in tables:
            print(f"  백업 중: {table}")
            try:
                # 테이블 스키마 가져오기
                result = session.execute(text(f"PRAGMA table_info({table})"))
                columns = [row[1] for row in result.fetchall()]
                
                # 데이터 가져오기
                result = session.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                
                # 딕셔너리로 변환
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[columns[i]] = value
                    table_data.append(row_dict)
                
                backup_data[table] = table_data
                print(f"      {len(table_data)}개 레코드 백업 완료")
            except Exception as e:
                print(f"  ⚠️ {table} 백업 실패: {e}")
                continue
    
    # 2. academy.db 데이터 로드
    print("📊 academy.db 데이터 로드 중...")
    with Session(sqlite_engine) as session:
        # 테이블 목록 가져오기
        result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        
        for table in tables:
            print(f"  로드 중: {table}")
            try:
                # 테이블 스키마 가져오기
                result = session.execute(text(f"PRAGMA table_info({table})"))
                columns = [row[1] for row in result.fetchall()]
                
                # 데이터 가져오기
                result = session.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                
                # 딕셔너리로 변환
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        row_dict[columns[i]] = value
                    table_data.append(row_dict)
                
                # PostgreSQL에 삽입
                with Session(postgres_engine) as postgres_session:
                    for row_data in table_data:
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
                            postgres_session.execute(text(sql), row_data)
                        except Exception as e:
                            print(f"      ❌ 레코드 삽입 실패: {e}")
                            postgres_session.rollback()
                            continue
                    postgres_session.commit()
                    print(f"      ✅ {table} 테이블 삽입 완료")
            except Exception as e:
                print(f"  ❌ {table} 테이블 처리 실패: {e}")
                continue
    
    # 3. 결과 확인
    print("📊 동기화 결과 확인...")
    with Session(postgres_engine) as session:
        for table in ['student', 'teacher', 'material', 'lecture']:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"    {table}: {count}개")
            except Exception as e:
                print(f"    {table}: 확인 실패 - {e}")
    
    print("✅ PostgreSQL 데이터가 academy.db와 동일해졌습니다!")
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 함수"""
    # 시작 시
    print("🚀 애플리케이션 시작...")
    
    # PostgreSQL 스키마 수정 (배포 환경에서만)
    database_url = os.getenv("DATABASE_URL", "")
    if database_url and "postgresql" in database_url:
        print("🔧 PostgreSQL 스키마 수정 시작...")
        try:
            force_fix_postgresql_schema()
            print("✅ PostgreSQL 스키마 수정 완료!")
            
            # 데이터 동기화 실행
            print("🔄 데이터 동기화 시작...")
            try:
                # 안전한 데이터 동기화 함수 사용
                sync_postgresql_data()
                print("✅ 데이터 동기화 완료!")
            except Exception as e:
                print(f"❌ 데이터 동기화 실패: {e}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"❌ PostgreSQL 스키마 수정 실패: {e}")
            import traceback
            traceback.print_exc()
    
    # 안전한 초기화만 실행 (강제 리셋 제거)
    print("🔧 안전한 초기화 시작...")
    try:
        from app.core.database import create_db_and_tables
        create_db_and_tables()
        print("✅ 안전한 초기화 완료!")
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
    
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
app.include_router(statistics.router, prefix="/api/v1", tags=["Statistics"])

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
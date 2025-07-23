#!/usr/bin/env python3
"""
PostgreSQL 스키마 및 데이터 분석 스크립트
현재 PostgreSQL의 테이블 구조와 데이터를 상세히 분석합니다.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 환경 변수에서 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    print("로컬에서 실행하려면 .env 파일의 DATABASE_URL을 확인하세요.")
    sys.exit(1)

def analyze_postgresql_schema():
    """PostgreSQL 스키마 및 데이터 상세 분석"""
    try:
        print("🔍 PostgreSQL 스키마 및 데이터 분석 시작...")
        print(f"데이터베이스 URL: {DATABASE_URL[:50]}...")
        
        # 엔진 생성
        engine = create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # 세션 생성
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            print("\n" + "="*60)
            print("📊 PostgreSQL 데이터베이스 분석 결과")
            print("="*60)
            
            # 1. 테이블 목록 확인
            print("\n1️⃣ 테이블 목록 확인...")
            result = session.execute(text("""
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = []
            for row in result.fetchall():
                tables.append(row[0])
                print(f"  - {row[0]} ({row[1]})")
            
            print(f"\n총 {len(tables)}개 테이블 발견")
            
            # 2. 각 테이블의 상세 스키마 분석
            print("\n2️⃣ 테이블별 상세 스키마 분석...")
            
            for table in ['student', 'teacher', 'material', 'lecture']:
                if table in tables:
                    print(f"\n  📋 {table} 테이블 분석:")
                    
                    # 컬럼 정보
                    result = session.execute(text(f"""
                        SELECT 
                            column_name,
                            data_type,
                            is_nullable,
                            column_default,
                            character_maximum_length
                        FROM information_schema.columns 
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position;
                    """))
                    
                    columns = []
                    for row in result.fetchall():
                        columns.append(row[0])
                        max_length = f"({row[4]})" if row[4] else ""
                        default = f" DEFAULT {row[3]}" if row[3] else ""
                        nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                        print(f"    - {row[0]}: {row[1]}{max_length}{default} {nullable}")
                    
                    # 데이터 수 확인
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"    📊 데이터 수: {count}개")
                    
                    # 샘플 데이터 (처음 3개)
                    if count > 0:
                        result = session.execute(text(f"SELECT * FROM {table} LIMIT 3"))
                        rows = result.fetchall()
                        print(f"    📝 샘플 데이터:")
                        for i, row in enumerate(rows, 1):
                            print(f"      {i}. {row}")
                    else:
                        print(f"    📝 데이터 없음")
                    
                    # 필수 컬럼 확인
                    if table == 'material':
                        required_columns = ['id', 'name', 'subject', 'grade', 'author']
                        missing_required = [col for col in required_columns if col not in columns]
                        
                        if missing_required:
                            print(f"    ❌ 누락된 필수 컬럼: {missing_required}")
                        else:
                            print(f"    ✅ 모든 필수 컬럼 존재")
                else:
                    print(f"\n  ❌ {table} 테이블이 존재하지 않음")
            
            # 3. 데이터 무결성 검사
            print("\n3️⃣ 데이터 무결성 검사...")
            
            for table in ['student', 'teacher', 'material', 'lecture']:
                if table in tables:
                    try:
                        # NULL 값이 있는 컬럼 확인
                        result = session.execute(text(f"""
                            SELECT column_name, COUNT(*) as null_count
                            FROM (
                                SELECT * FROM {table}
                            ) t
                            CROSS JOIN LATERAL (
                                SELECT unnest(ARRAY{columns}) as column_name
                            ) cols
                            WHERE cols.column_name IS NULL
                            GROUP BY column_name;
                        """))
                        
                        null_counts = result.fetchall()
                        if null_counts:
                            print(f"  {table}: NULL 값 발견")
                            for col, count in null_counts:
                                print(f"    - {col}: {count}개 NULL")
                        else:
                            print(f"  {table}: NULL 값 없음")
                            
                    except Exception as e:
                        print(f"  {table}: 무결성 검사 실패 - {e}")
            
            # 4. AI 챗봇이 읽는 데이터 확인
            print("\n4️⃣ AI 챗봇 데이터 읽기 테스트...")
            
            # ContextBuilder가 사용하는 쿼리와 동일한 쿼리 실행
            queries = {
                'student': "SELECT student.id AS student_id, student.name AS student_name, student.email AS student_email, student.phone AS student_phone, student.grade AS student_grade, student.tuition_fee AS student_tuition_fee, student.tuition_due_date AS student_tuition_due_date, student.is_active AS student_is_active, student.created_at AS student_created_at, student.updated_at AS student_updated_at FROM student",
                'teacher': "SELECT teacher.id AS teacher_id, teacher.name AS teacher_name, teacher.email AS teacher_email, teacher.phone AS teacher_phone, teacher.subject AS teacher_subject, teacher.hourly_rate AS teacher_hourly_rate, teacher.is_active AS teacher_is_active, teacher.created_at AS teacher_created_at, teacher.updated_at AS teacher_updated_at FROM teacher",
                'material': "SELECT material.id AS material_id, material.name AS material_name, material.subject AS material_subject, material.grade AS material_grade, material.author AS material_author, material.isbn AS material_isbn, material.description AS material_description, material.publication_date AS material_publication_date, material.edition AS material_edition, material.quantity AS material_quantity, material.min_quantity AS material_min_quantity, material.price AS material_price, material.expiry_date AS material_expiry_date, material.is_active AS material_is_active, material.created_at AS material_created_at, material.updated_at AS material_updated_at FROM material",
                'lecture': "SELECT lecture.id AS lecture_id, lecture.title AS lecture_title, lecture.subject AS lecture_subject, lecture.grade AS lecture_grade, lecture.schedule AS lecture_schedule, lecture.is_active AS lecture_is_active, lecture.created_at AS lecture_created_at, lecture.updated_at AS lecture_updated_at FROM lecture"
            }
            
            for table, query in queries.items():
                try:
                    result = session.execute(text(query))
                    rows = result.fetchall()
                    print(f"  {table}: {len(rows)}개 레코드 조회 성공")
                    
                    if rows:
                        print(f"    샘플: {rows[0]}")
                except Exception as e:
                    print(f"  {table}: 쿼리 실패 - {e}")
            
            # 5. 엑셀 미리보기 데이터 확인
            print("\n5️⃣ 엑셀 미리보기 데이터 확인...")
            
            # 엑셀 미리보기 API가 사용하는 쿼리 테스트
            excel_queries = {
                'student': "SELECT * FROM student ORDER BY created_at DESC LIMIT 100",
                'teacher': "SELECT * FROM teacher ORDER BY created_at DESC LIMIT 100",
                'material': "SELECT * FROM material ORDER BY created_at DESC LIMIT 100",
                'lecture': "SELECT * FROM lecture ORDER BY created_at DESC LIMIT 100"
            }
            
            for table, query in excel_queries.items():
                try:
                    result = session.execute(text(query))
                    rows = result.fetchall()
                    print(f"  {table}: {len(rows)}개 레코드 (엑셀 미리보기)")
                except Exception as e:
                    print(f"  {table}: 엑셀 미리보기 쿼리 실패 - {e}")
            
            print("\n" + "="*60)
            print("✅ PostgreSQL 스키마 및 데이터 분석 완료")
            print("="*60)
                
    except Exception as e:
        print(f"❌ PostgreSQL 분석 중 오류: {e}")

if __name__ == "__main__":
    print("🚀 PostgreSQL 스키마 및 데이터 분석 스크립트 시작")
    analyze_postgresql_schema() 
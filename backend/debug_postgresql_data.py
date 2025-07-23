#!/usr/bin/env python3
"""
PostgreSQL 데이터 내용 상세 분석
academy.db와 PostgreSQL 데이터 비교
"""

import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def debug_postgresql_data():
    """PostgreSQL 데이터 상세 분석"""
    
    # 환경 변수에서 데이터베이스 URL 가져오기
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
        return
    
    if "sqlite" in database_url:
        print("❌ SQLite 데이터베이스입니다. PostgreSQL을 확인해주세요.")
        return
    
    try:
        print("🔍 PostgreSQL vs academy.db 데이터 비교 분석...")
        
        # 1. 로컬 academy.db 데이터 확인
        print("\n📊 로컬 academy.db 데이터:")
        if os.path.exists('academy.db'):
            conn = sqlite3.connect('academy.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM student')
            local_students = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM teacher') 
            local_teachers = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM material')
            local_materials = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM lecture')
            local_lectures = cursor.fetchone()[0]
            
            print(f"  학생: {local_students}명")
            print(f"  강사: {local_teachers}명") 
            print(f"  교재: {local_materials}개")
            print(f"  강의: {local_lectures}개")
            
            # 학생 이름 샘플
            cursor.execute('SELECT name FROM student LIMIT 10')
            local_student_names = [row[0] for row in cursor.fetchall()]
            print(f"  학생 샘플: {local_student_names[:5]}")
            
            conn.close()
        else:
            print("  ❌ academy.db 파일이 없습니다.")
        
        # 2. PostgreSQL 데이터 확인
        print("\n📊 PostgreSQL 데이터:")
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # 개수 확인
            result = session.execute(text("SELECT COUNT(*) FROM student"))
            pg_students = result.scalar()
            
            result = session.execute(text("SELECT COUNT(*) FROM teacher"))
            pg_teachers = result.scalar()
            
            result = session.execute(text("SELECT COUNT(*) FROM material"))
            pg_materials = result.scalar()
            
            result = session.execute(text("SELECT COUNT(*) FROM lecture"))
            pg_lectures = result.scalar()
            
            print(f"  학생: {pg_students}명")
            print(f"  강사: {pg_teachers}명")
            print(f"  교재: {pg_materials}개") 
            print(f"  강의: {pg_lectures}개")
            
            # 학생 이름 샘플
            result = session.execute(text("SELECT name FROM student ORDER BY id LIMIT 10"))
            pg_student_names = [row[0] for row in result.fetchall()]
            print(f"  학생 샘플: {pg_student_names[:5]}")
            
            # 3. 중복 데이터 확인
            print("\n🔍 중복 데이터 분석:")
            
            # 같은 이름의 학생이 여러 명 있는지 확인
            result = session.execute(text("""
                SELECT name, COUNT(*) as count 
                FROM student 
                GROUP BY name 
                HAVING COUNT(*) > 1
                ORDER BY count DESC
            """))
            duplicates = result.fetchall()
            if duplicates:
                print("  중복 학생 이름:")
                for name, count in duplicates:
                    print(f"    {name}: {count}명")
            else:
                print("  ✅ 중복 학생 이름 없음")
            
            # 교재 중복 확인
            result = session.execute(text("""
                SELECT name, COUNT(*) as count 
                FROM material 
                GROUP BY name 
                HAVING COUNT(*) > 1
                ORDER BY count DESC
            """))
            material_duplicates = result.fetchall()
            if material_duplicates:
                print("  중복 교재 이름:")
                for name, count in material_duplicates:
                    print(f"    {name}: {count}개")
            else:
                print("  ✅ 중복 교재 이름 없음")
            
            # 4. 특정 학생 확인 (academy.db vs PostgreSQL)
            print("\n🔍 특정 학생 비교:")
            if os.path.exists('academy.db'):
                # 로컬에서 첫 번째 학생
                conn = sqlite3.connect('academy.db')
                cursor = conn.cursor()
                cursor.execute('SELECT name, email FROM student LIMIT 1')
                local_first = cursor.fetchone()
                conn.close()
                
                if local_first:
                    print(f"  로컬 첫 번째 학생: {local_first[0]} ({local_first[1]})")
                    
                    # PostgreSQL에서 같은 학생 찾기
                    result = session.execute(text("SELECT name, email FROM student WHERE name = :name"), 
                                           {"name": local_first[0]})
                    pg_match = result.fetchone()
                    
                    if pg_match:
                        print(f"  PostgreSQL에서 발견: {pg_match[0]} ({pg_match[1]})")
                        print("  ✅ 로컬 데이터가 PostgreSQL에 존재")
                    else:
                        print("  ❌ PostgreSQL에서 찾을 수 없음")
        
        print("\n✅ 데이터 비교 분석 완료!")
        
    except Exception as e:
        print(f"❌ 데이터 분석 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_postgresql_data() 
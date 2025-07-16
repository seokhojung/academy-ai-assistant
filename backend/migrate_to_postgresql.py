#!/usr/bin/env python3
"""
SQLite에서 PostgreSQL로 데이터 마이그레이션 스크립트
"""

import sqlite3
import os
import json
from datetime import datetime
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.material import Material
from app.models.user import User

def backup_sqlite_data():
    """SQLite 데이터를 JSON으로 백업"""
    print("SQLite 데이터 백업 중...")
    
    # SQLite 연결
    sqlite_path = "./academy_ai.db"
    if not os.path.exists(sqlite_path):
        print(f"SQLite 파일을 찾을 수 없습니다: {sqlite_path}")
        return None
    
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # 테이블 목록 조회
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    backup_data = {}
    
    for table in tables:
        table_name = table[0]
        if table_name == 'sqlite_sequence':
            continue
            
        print(f"테이블 백업 중: {table_name}")
        
        # 테이블 데이터 조회
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # 컬럼명 조회
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 데이터를 딕셔너리로 변환
        table_data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            table_data.append(row_dict)
        
        backup_data[table_name] = table_data
    
    conn.close()
    
    # JSON 파일로 저장
    backup_file = f"sqlite_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"백업 완료: {backup_file}")
    return backup_data

def migrate_to_postgresql(backup_data):
    """PostgreSQL로 데이터 마이그레이션"""
    print("PostgreSQL로 데이터 마이그레이션 중...")
    
    # PostgreSQL 엔진 생성
    pg_engine = create_engine(
        settings.database_url,
        echo=True,
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    # 테이블 생성
    SQLModel.metadata.create_all(pg_engine)
    
    with Session(pg_engine) as session:
        try:
            # 사용자 데이터 마이그레이션
            if 'user' in backup_data:
                print("사용자 데이터 마이그레이션 중...")
                for user_data in backup_data['user']:
                    # id 필드 제거 (자동 생성)
                    if 'id' in user_data:
                        del user_data['id']
                    
                    user = User(**user_data)
                    session.add(user)
                
                session.commit()
                print(f"사용자 {len(backup_data['user'])}명 마이그레이션 완료")
            
            # 교사 데이터 마이그레이션
            if 'teacher' in backup_data:
                print("교사 데이터 마이그레이션 중...")
                for teacher_data in backup_data['teacher']:
                    if 'id' in teacher_data:
                        del teacher_data['id']
                    
                    teacher = Teacher(**teacher_data)
                    session.add(teacher)
                
                session.commit()
                print(f"교사 {len(backup_data['teacher'])}명 마이그레이션 완료")
            
            # 학생 데이터 마이그레이션
            if 'student' in backup_data:
                print("학생 데이터 마이그레이션 중...")
                for student_data in backup_data['student']:
                    if 'id' in student_data:
                        del student_data['id']
                    
                    student = Student(**student_data)
                    session.add(student)
                
                session.commit()
                print(f"학생 {len(backup_data['student'])}명 마이그레이션 완료")
            
            # 자료 데이터 마이그레이션
            if 'material' in backup_data:
                print("자료 데이터 마이그레이션 중...")
                for material_data in backup_data['material']:
                    if 'id' in material_data:
                        del material_data['id']
                    
                    material = Material(**material_data)
                    session.add(material)
                
                session.commit()
                print(f"자료 {len(backup_data['material'])}개 마이그레이션 완료")
            
            print("모든 데이터 마이그레이션 완료!")
            
        except Exception as e:
            session.rollback()
            print(f"마이그레이션 중 오류 발생: {e}")
            raise

def main():
    """메인 실행 함수"""
    print("=== SQLite to PostgreSQL 마이그레이션 시작 ===")
    
    # 1. SQLite 데이터 백업
    backup_data = backup_sqlite_data()
    if not backup_data:
        print("백업할 데이터가 없습니다.")
        return
    
    # 2. PostgreSQL로 마이그레이션
    try:
        migrate_to_postgresql(backup_data)
        print("마이그레이션 성공!")
    except Exception as e:
        print(f"마이그레이션 실패: {e}")
        print("백업 파일을 확인하여 수동으로 데이터를 복원하세요.")

if __name__ == "__main__":
    main() 
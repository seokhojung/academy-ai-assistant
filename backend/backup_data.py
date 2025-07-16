#!/usr/bin/env python3
"""
데이터 백업 스크립트
서버 중지 전에 데이터를 백업합니다.
"""

import sqlite3
import json
import os
from datetime import datetime

def backup_students():
    """학생 데이터를 백업합니다."""
    try:
        # SQLite 데이터베이스 연결
        conn = sqlite3.connect('./academy.db')
        cursor = conn.cursor()
        
        # 학생 데이터 조회
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()
        
        # 컬럼명 가져오기
        columns = [description[0] for description in cursor.description]
        
        # 데이터를 딕셔너리로 변환
        student_data = []
        for student in students:
            student_dict = dict(zip(columns, student))
            student_data.append(student_dict)
        
        # JSON 파일로 백업
        backup_dir = './backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'{backup_dir}/students_backup_{timestamp}.json'
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(student_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 학생 데이터 백업 완료: {backup_file}")
        print(f"📊 백업된 학생 수: {len(student_data)}명")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 백업 실패: {e}")
        return False

def restore_students(backup_file):
    """백업 파일에서 학생 데이터를 복원합니다."""
    try:
        # 백업 파일 읽기
        with open(backup_file, 'r', encoding='utf-8') as f:
            student_data = json.load(f)
        
        # SQLite 데이터베이스 연결
        conn = sqlite3.connect('./academy.db')
        cursor = conn.cursor()
        
        # 기존 데이터 삭제
        cursor.execute("DELETE FROM student")
        
        # 백업 데이터 복원
        for student in student_data:
            cursor.execute("""
                INSERT INTO student (name, email, phone, grade, tuition_fee, tuition_due_date, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student['name'],
                student['email'],
                student['phone'],
                student['grade'],
                student['tuition_fee'],
                student['tuition_due_date'],
                student['is_active'],
                student['created_at'],
                student['updated_at']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ 학생 데이터 복원 완료: {backup_file}")
        print(f"📊 복원된 학생 수: {len(student_data)}명")
        
        return True
        
    except Exception as e:
        print(f"❌ 복원 실패: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        if len(sys.argv) > 2:
            backup_file = sys.argv[2]
            restore_students(backup_file)
        else:
            print("사용법: python backup_data.py restore <backup_file>")
    else:
        backup_students() 
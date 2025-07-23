#!/usr/bin/env python3
"""
간단한 샘플 데이터 추가 스크립트
"""
import sqlite3
import os
from datetime import datetime

def add_sample_data():
    """SQLite 데이터베이스에 직접 샘플 데이터 추가"""
    db_path = "academy.db"
    
    # 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 샘플 데이터 추가 시작 ===")
    
    try:
        # 강사 데이터 추가
        teachers_data = [
            ("김수학", "수학", "kim.math@academy.com", "010-1234-5678"),
            ("이영어", "영어", "lee.english@academy.com", "010-2345-6789"),
            ("박과학", "과학", "park.science@academy.com", "010-3456-7890"),
            ("최국어", "국어", "choi.korean@academy.com", "010-4567-8901"),
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO teacher (name, subject, email, phone)
            VALUES (?, ?, ?, ?)
        """, teachers_data)
        
        print(f"✅ {len(teachers_data)}명의 강사 데이터 추가 완료")
        
        # 교재 데이터 추가
        materials_data = [
            ("중등 수학 기초", "수학", "중1", "김수학", "수학출판사"),
            ("고등 영어 독해", "영어", "고1", "이영어", "영어출판사"),
            ("중등 과학 실험", "과학", "중2", "박과학", "과학출판사"),
            ("고등 국어 문학", "국어", "고2", "최국어", "국어출판사"),
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO material (name, subject, grade, author, publisher)
            VALUES (?, ?, ?, ?, ?)
        """, materials_data)
        
        print(f"✅ {len(materials_data)}개의 교재 데이터 추가 완료")
        
        # 학생 데이터 추가
        students_data = [
            ("김학생", "중1", "kim.student@email.com", "010-1111-2222"),
            ("이학생", "고1", "lee.student@email.com", "010-2222-3333"),
            ("박학생", "중2", "park.student@email.com", "010-3333-4444"),
            ("최학생", "고2", "choi.student@email.com", "010-4444-5555"),
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO student (name, grade, email, phone)
            VALUES (?, ?, ?, ?)
        """, students_data)
        
        print(f"✅ {len(students_data)}명의 학생 데이터 추가 완료")
        
        # 강의 데이터 추가
        lectures_data = [
            ("중등 수학 기초반", "수학", "중1", 15, 8, 150000, "월수금 14:00-16:00", "A-101", True, "중학교 1학년 수학 기초 과정"),
            ("고등 영어 독해반", "영어", "고1", 12, 10, 180000, "화목 16:00-18:00", "B-201", True, "고등학교 1학년 영어 독해 과정"),
            ("중등 과학 실험반", "과학", "중2", 10, 6, 200000, "토 10:00-12:00", "실험실-1", True, "중학교 2학년 과학 실험 과정"),
            ("고등 국어 문학반", "국어", "고2", 15, 12, 160000, "월수 19:00-21:00", "C-301", True, "고등학교 2학년 국어 문학 과정"),
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO lecture (title, subject, grade, max_students, current_students, tuition_fee, schedule, classroom, is_active, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, lectures_data)
        
        print(f"✅ {len(lectures_data)}개의 강의 데이터 추가 완료")
        
        # 변경사항 저장
        conn.commit()
        print("✅ 모든 데이터가 성공적으로 추가되었습니다!")
        
        # 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM teacher")
        teacher_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM material")
        material_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM student")
        student_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM lecture")
        lecture_count = cursor.fetchone()[0]
        
        print(f"\n📊 현재 데이터베이스 상태:")
        print(f"   강사: {teacher_count}명")
        print(f"   교재: {material_count}개")
        print(f"   학생: {student_count}명")
        print(f"   강의: {lecture_count}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_sample_data() 
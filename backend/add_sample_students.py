#!/usr/bin/env python3
"""
학생 샘플 데이터 추가 스크립트 (50명)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_session, create_db_and_tables
from app.models.student import Student
from sqlmodel import Session, select, delete
import random
from datetime import datetime, timedelta
import traceback
from app.core import config

def log_message(message):
    """메시지를 콘솔과 파일에 동시에 출력"""
    print(message, flush=True)
    with open("sample_students_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def add_sample_students():
    """학생 샘플 데이터를 데이터베이스에 추가 (50명)"""
    log_message("=== 학생 샘플 데이터 추가 시작 (50명) ===")
    log_message(f"[DEBUG] DB URL: {getattr(config.settings, 'database_url', None)}")
    
    try:
        create_db_and_tables()
        log_message("✓ DB 테이블 생성 완료")
        
        with next(get_session()) as session:
            # 기존 데이터 삭제
            existing_students = session.exec(select(Student)).all()
            log_message(f"기존 학생 수: {len(existing_students)}")
            
            if len(existing_students) > 0:
                log_message("기존 학생 데이터를 삭제합니다...")
                session.execute(delete(Student))
                session.commit()
                log_message("✓ 기존 학생 데이터 삭제 완료")
            
            # 현실적인 한국 학생 이름들
            first_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안', '송', '류', '전']
            last_names = ['민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호', '지후', '준서', '준우', '현우', '도현', '지훈', '우진', '민재', '건우', '서진', '현준', '도훈', '지원', '재민', '재현', '재원', '재준']
            
            # 학년별 분포
            grades = ['중1', '중2', '중3', '고1', '고2', '고3']
            grade_weights = [0.15, 0.18, 0.20, 0.22, 0.15, 0.10]
            
            # 수강료 분포
            tuition_ranges = [
                {'min': 130000, 'max': 150000, 'weight': 0.2},
                {'min': 150000, 'max': 180000, 'weight': 0.3},
                {'min': 180000, 'max': 200000, 'weight': 0.25},
                {'min': 200000, 'max': 220000, 'weight': 0.15},
                {'min': 220000, 'max': 250000, 'weight': 0.1}
            ]
            
            students_to_add = []
            
            for i in range(50):
                # 랜덤 이름 생성
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                full_name = first_name + last_name
                
                # 가중치 기반 학년 선택
                grade = random.choices(grades, weights=grade_weights)[0]
                
                # 가중치 기반 수강료 선택
                tuition_range = random.choices(tuition_ranges, weights=[r['weight'] for r in tuition_ranges])[0]
                tuition_fee = random.randint(tuition_range['min'], tuition_range['max'])
                
                # 납부일 (현재 날짜 기준 ±30일)
                days_offset = random.randint(-30, 30)
                due_date = datetime.now() + timedelta(days=days_offset)
                
                # 활성 상태 (85% 활성)
                is_active = random.random() > 0.15
                
                student_data = {
                    "name": full_name,
                    "email": f"{full_name.lower()}{i+1}@academy.com",
                    "phone": f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "grade": grade,
                    "tuition_fee": tuition_fee,
                    "tuition_due_date": due_date,
                    "is_active": is_active
                }
                
                students_to_add.append(student_data)
            
            # 학생 데이터 추가
            for student_data in students_to_add:
                student = Student(**student_data)
                session.add(student)
                log_message(f"학생 추가: {student_data['name']} ({student_data['grade']}) - {student_data['tuition_fee']:,}원")
            
            session.commit()
            log_message(f"✓ 총 {len(students_to_add)}명의 학생 데이터 추가 완료")
            
            # 추가된 데이터 확인
            total_students = session.exec(select(Student)).all()
            log_message(f"✓ DB에 총 {len(total_students)}명의 학생이 등록됨")
            
            # 활성/비활성 학생 수 확인
            active_count = sum(1 for s in total_students if s.is_active)
            inactive_count = sum(1 for s in total_students if not s.is_active)
            log_message(f"활성 학생: {active_count}명, 비활성 학생: {inactive_count}명")
            
    except Exception as e:
        log_message(f"❌ 오류 발생: {str(e)}")
        log_message(f"상세 오류: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    add_sample_students() 
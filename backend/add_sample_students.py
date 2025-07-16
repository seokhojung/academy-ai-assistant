#!/usr/bin/env python3
"""
샘플 학생 50명을 데이터베이스에 추가하는 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_session
from app.models.student import Student
from sqlmodel import Session
import random
from datetime import datetime, timedelta
import traceback

def add_sample_students():
    """샘플 학생 50명을 데이터베이스에 추가"""
    
    # 현실적인 한국 학생 이름들
    first_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안', '송', '류', '전']
    last_names = ['민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호', '지후', '준서', '준우', '현우', '도현', '지훈', '우진', '민재', '건우', '서진', '현준', '도훈', '지원', '재민', '재현', '재원', '재준']
    
    # 학년별 분포
    grades = ['1학년', '2학년', '3학년', '4학년', '5학년', '6학년']
    grade_weights = [0.15, 0.18, 0.20, 0.22, 0.15, 0.10]
    
    # 수강료 분포
    tuition_ranges = [
        {'min': 300000, 'max': 400000, 'weight': 0.2},
        {'min': 400000, 'max': 500000, 'weight': 0.3},
        {'min': 500000, 'max': 600000, 'weight': 0.25},
        {'min': 600000, 'max': 700000, 'weight': 0.15},
        {'min': 700000, 'max': 800000, 'weight': 0.1}
    ]
    
    db = next(get_session())
    
    try:
        # 기존 학생 수 확인
        existing_count = db.query(Student).count()
        print(f"기존 학생 수: {existing_count}명")
        
        if existing_count >= 50:
            print("이미 50명 이상의 학생이 있습니다.")
            return
        
        to_add = 50 - existing_count
        print(f"추가할 학생 수: {to_add}명")
        
        students_to_add = []
        
        for i in range(to_add):
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
            due_date_str = due_date.strftime('%Y-%m-%d')
            
            # 활성 상태 (85% 활성)
            is_active = random.random() > 0.15
            
            student = Student(
                name=full_name,
                email=f"{full_name.lower()}{i+1}@academy.com",
                phone=f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                grade=grade,
                tuition_fee=tuition_fee,
                tuition_due_date=due_date,
                is_active=is_active
            )
            
            students_to_add.append(student)
        
        # 일괄 추가
        db.add_all(students_to_add)
        db.commit()
        
        print(f"✅ {to_add}명의 샘플 학생이 성공적으로 추가되었습니다!")
        print(f"총 학생 수: {db.query(Student).count()}명")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_students() 
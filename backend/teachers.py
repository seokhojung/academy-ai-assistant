#!/usr/bin/env python3
"""
강사 샘플 데이터 추가 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_session, create_db_and_tables
from app.models.teacher import Teacher
from sqlmodel import Session, select
import random
from datetime import datetime, timedelta
import traceback
from app.core import config

def log_message(message):
    """메시지를 콘솔과 파일에 동시에 출력"""
    print(message, flush=True)
    with open("sample_teachers_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def add_sample_teachers():
    """강사 샘플 데이터를 데이터베이스에 추가"""
    log_message("=== 강사 샘플 데이터 추가 시작 ===")
    log_message(f"[DEBUG] DB URL: {getattr(config.settings, 'database_url', None)}")
    
    try:
        create_db_and_tables()
        log_message("✓ DB 테이블 생성 완료")
        
        with next(get_session()) as session:
            # 기존 데이터 확인
            existing_teachers = session.exec(select(Teacher)).all()
            log_message(f"기존 강사 수: {len(existing_teachers)}")
            
            if len(existing_teachers) > 0:
                log_message("이미 강사 데이터가 존재합니다. 건너뜁니다.")
                return
            
            # 샘플 강사 데이터
            sample_teachers = [
                {
                    "name": "김수학",
                    "email": "kim.math@academy.com",
                    "phone": "010-1111-2222",
                    "subject": "수학",
                    "hourly_rate": 50000,
                    "is_active": True
                },
                {
                    "name": "이영어",
                    "email": "lee.english@academy.com",
                    "phone": "010-2222-3333",
                    "subject": "영어",
                    "hourly_rate": 45000,
                    "is_active": True
                },
                {
                    "name": "박과학",
                    "email": "park.science@academy.com",
                    "phone": "010-3333-4444",
                    "subject": "과학",
                    "hourly_rate": 48000,
                    "is_active": True
                },
                {
                    "name": "최국어",
                    "email": "choi.korean@academy.com",
                    "phone": "010-4444-5555",
                    "subject": "국어",
                    "hourly_rate": 42000,
                    "is_active": True
                },
                {
                    "name": "정사회",
                    "email": "jung.social@academy.com",
                    "phone": "010-5555-6666",
                    "subject": "사회",
                    "hourly_rate": 40000,
                    "is_active": True
                },
                {
                    "name": "강역사",
                    "email": "kang.history@academy.com",
                    "phone": "010-6666-7777",
                    "subject": "역사",
                    "hourly_rate": 38000,
                    "is_active": True
                },
                {
                    "name": "조물리",
                    "email": "cho.physics@academy.com",
                    "phone": "010-7777-8888",
                    "subject": "물리",
                    "hourly_rate": 52000,
                    "is_active": True
                },
                {
                    "name": "윤화학",
                    "email": "yoon.chemistry@academy.com",
                    "phone": "010-8888-9999",
                    "subject": "화학",
                    "hourly_rate": 50000,
                    "is_active": True
                },
                {
                    "name": "장생물",
                    "email": "jang.biology@academy.com",
                    "phone": "010-9999-0000",
                    "subject": "생물",
                    "hourly_rate": 47000,
                    "is_active": True
                },
                {
                    "name": "임지구",
                    "email": "lim.earth@academy.com",
                    "phone": "010-0000-1111",
                    "subject": "지구과학",
                    "hourly_rate": 46000,
                    "is_active": True
                }
            ]
            
            # 강사 데이터 추가
            for teacher_data in sample_teachers:
                teacher = Teacher(**teacher_data)
                session.add(teacher)
                log_message(f"강사 추가: {teacher_data['name']} ({teacher_data['subject']})")
            
            session.commit()
            log_message(f"✓ 총 {len(sample_teachers)}명의 강사 데이터 추가 완료")
            
            # 추가된 데이터 확인
            total_teachers = session.exec(select(Teacher)).all()
            log_message(f"✓ DB에 총 {len(total_teachers)}명의 강사가 등록됨")
            
    except Exception as e:
        log_message(f"❌ 오류 발생: {str(e)}")
        log_message(f"상세 오류: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    add_sample_teachers() 
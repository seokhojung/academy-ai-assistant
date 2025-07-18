#!/usr/bin/env python3
"""
강의 샘플 데이터 추가 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_session, create_db_and_tables
from app.models.lecture import Lecture
from sqlmodel import Session, select
import random
from datetime import datetime, timedelta
import traceback
from app.core import config

def log_message(message):
    """메시지를 콘솔과 파일에 동시에 출력"""
    print(message, flush=True)
    with open("sample_lectures_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def add_sample_lectures():
    """강의 샘플 데이터를 데이터베이스에 추가"""
    log_message("=== 강의 샘플 데이터 추가 시작 ===")
    log_message(f"[DEBUG] DB URL: {getattr(config.settings, 'database_url', None)}")
    
    try:
        create_db_and_tables()  # 테이블이 없으면 생성
        log_message("✅ 데이터베이스 테이블 생성/확인 완료")
    except Exception as e:
        log_message(f"❌ 테이블 생성 오류: {e}")
        return
    
    # 강의 샘플 데이터
    sample_lectures = [
        {
            "title": "중등 수학 기초반",
            "subject": "수학",
            "grade": "중1",
            "max_students": 15,
            "current_students": 8,
            "tuition_fee": 150000,
            "schedule": "월수금 14:00-16:00",
            "classroom": "A-101",
            "is_active": True,
            "description": "중학교 1학년 수학 기초 과정"
        },
        {
            "title": "고등 영어 독해반",
            "subject": "영어",
            "grade": "고1",
            "max_students": 12,
            "current_students": 10,
            "tuition_fee": 180000,
            "schedule": "화목 16:00-18:00",
            "classroom": "B-201",
            "is_active": True,
            "description": "고등학교 1학년 영어 독해 과정"
        },
        {
            "title": "중등 과학 실험반",
            "subject": "과학",
            "grade": "중2",
            "max_students": 10,
            "current_students": 6,
            "tuition_fee": 200000,
            "schedule": "토 10:00-12:00",
            "classroom": "실험실-1",
            "is_active": True,
            "description": "중학교 2학년 과학 실험 과정"
        },
        {
            "title": "고등 국어 문학반",
            "subject": "국어",
            "grade": "고2",
            "max_students": 15,
            "current_students": 12,
            "tuition_fee": 160000,
            "schedule": "월수 19:00-21:00",
            "classroom": "C-301",
            "is_active": True,
            "description": "고등학교 2학년 국어 문학 과정"
        },
        {
            "title": "중등 사회 탐구반",
            "subject": "사회",
            "grade": "중3",
            "max_students": 12,
            "current_students": 9,
            "tuition_fee": 140000,
            "schedule": "화목 15:00-17:00",
            "classroom": "A-102",
            "is_active": True,
            "description": "중학교 3학년 사회 탐구 과정"
        },
        {
            "title": "고등 물리 심화반",
            "subject": "물리",
            "grade": "고3",
            "max_students": 8,
            "current_students": 7,
            "tuition_fee": 250000,
            "schedule": "금토 14:00-16:00",
            "classroom": "실험실-2",
            "is_active": True,
            "description": "고등학교 3학년 물리 심화 과정"
        },
        {
            "title": "중등 화학 기초반",
            "subject": "화학",
            "grade": "중2",
            "max_students": 10,
            "current_students": 5,
            "tuition_fee": 180000,
            "schedule": "토 14:00-16:00",
            "classroom": "실험실-3",
            "is_active": True,
            "description": "중학교 2학년 화학 기초 과정"
        },
        {
            "title": "고등 생명과학반",
            "subject": "생물",
            "grade": "고2",
            "max_students": 12,
            "current_students": 8,
            "tuition_fee": 190000,
            "schedule": "월수 16:00-18:00",
            "classroom": "실험실-4",
            "is_active": True,
            "description": "고등학교 2학년 생명과학 과정"
        },
        {
            "title": "중등 지구과학반",
            "subject": "지구과학",
            "grade": "중1",
            "max_students": 15,
            "current_students": 11,
            "tuition_fee": 160000,
            "schedule": "화목 14:00-16:00",
            "classroom": "A-103",
            "is_active": True,
            "description": "중학교 1학년 지구과학 과정"
        },
        {
            "title": "고등 수학 심화반",
            "subject": "수학",
            "grade": "고3",
            "max_students": 10,
            "current_students": 9,
            "tuition_fee": 220000,
            "schedule": "월수금 19:00-21:00",
            "classroom": "B-202",
            "is_active": True,
            "description": "고등학교 3학년 수학 심화 과정"
        }
    ]
    
    db = next(get_session())
    
    try:
        # 기존 강의 수 확인
        existing_count = len(db.exec(select(Lecture)).all())
        log_message(f"기존 강의 수: {existing_count}개")
        
        if existing_count >= 10:
            log_message("이미 10개 이상의 강의가 있습니다.")
            return
        
        to_add = 10 - existing_count
        log_message(f"추가할 강의 수: {to_add}개")
        
        lectures_to_add = []
        
        for i, lecture_data in enumerate(sample_lectures[:to_add]):
            # 기존 강의 확인
            existing_lecture = db.exec(select(Lecture).where(Lecture.title == lecture_data["title"])).first()
            if existing_lecture:
                log_message(f"이미 존재하는 강의: {lecture_data['title']}")
                continue
                
            lecture = Lecture(**lecture_data)
            lectures_to_add.append(lecture)
            log_message(f"강의 추가: {lecture_data['title']} - {lecture_data['subject']}")
        
        # 일괄 추가
        if lectures_to_add:
            db.add_all(lectures_to_add)
            db.commit()
            log_message(f"✅ {len(lectures_to_add)}개의 샘플 강의가 성공적으로 추가되었습니다!")
        else:
            log_message("추가할 강의가 없습니다.")
        
        # 최종 확인
        final_count = len(db.exec(select(Lecture)).all())
        log_message(f"총 강의 수: {final_count}개")
        
        # 추가된 강의 목록 출력
        all_lectures = db.exec(select(Lecture)).all()
        log_message("=== 현재 DB의 모든 강의 ===")
        for lecture in all_lectures:
            log_message(f"- {lecture.title} ({lecture.subject}, {lecture.grade})")
        
    except Exception as e:
        log_message(f"❌ 오류 발생: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
        log_message("=== 강의 샘플 데이터 추가 완료 ===")

if __name__ == "__main__":
    add_sample_lectures() 
#!/usr/bin/env python3
"""
교재 샘플 데이터 추가 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_session, create_db_and_tables
from app.models.material import Material
from sqlmodel import Session, select
import random
from datetime import datetime, timedelta
import traceback
from app.core import config

def log_message(message):
    """메시지를 콘솔과 파일에 동시에 출력"""
    print(message, flush=True)
    with open("sample_data_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def add_sample_materials():
    """교재 샘플 데이터를 데이터베이스에 추가"""
    log_message("=== 교재 샘플 데이터 추가 시작 ===")
    log_message(f"[DEBUG] DB URL: {getattr(config.settings, 'database_url', None)}")
    
    try:
        create_db_and_tables()  # 테이블이 없으면 생성
        log_message("✅ 데이터베이스 테이블 생성/확인 완료")
    except Exception as e:
        log_message(f"❌ 테이블 생성 오류: {e}")
        return
    
    # 교재 샘플 데이터
    sample_materials = [
        {
            "name": "중등 수학 1", "subject": "수학", "grade": "중1", 
            "publisher": "미래엔", "author": "미래엔 편집부", "isbn": "978-89-408-1234-5",
            "description": "중학교 1학년 수학 교과서", "edition": "2024년판",
            "quantity": 30, "min_quantity": 5, "price": 12000, "is_active": True
        },
        {
            "name": "중등 수학 2", "subject": "수학", "grade": "중2", 
            "publisher": "천재교육", "author": "천재교육 편집부", "isbn": "978-89-408-1235-2",
            "description": "중학교 2학년 수학 교과서", "edition": "2024년판",
            "quantity": 25, "min_quantity": 5, "price": 12500, "is_active": True
        },
        {
            "name": "고등 영어 독해", "subject": "영어", "grade": "고1", 
            "publisher": "YBM", "author": "YBM 편집부", "isbn": "978-89-408-1236-9",
            "description": "고등학교 1학년 영어 독해 교재", "edition": "2024년판",
            "quantity": 20, "min_quantity": 3, "price": 13500, "is_active": True
        },
        {
            "name": "중등 과학 실험", "subject": "과학", "grade": "중3", 
            "publisher": "비상교육", "author": "비상교육 편집부", "isbn": "978-89-408-1237-6",
            "description": "중학교 3학년 과학 실험 교재", "edition": "2024년판",
            "quantity": 18, "min_quantity": 5, "price": 14000, "is_active": True
        },
        {
            "name": "고등 국어 문학", "subject": "국어", "grade": "고2", 
            "publisher": "두산동아", "author": "두산동아 편집부", "isbn": "978-89-408-1238-3",
            "description": "고등학교 2학년 국어 문학 교재", "edition": "2024년판",
            "quantity": 15, "min_quantity": 3, "price": 15000, "is_active": True
        },
        {
            "name": "중등 사회 탐구", "subject": "사회", "grade": "중2", 
            "publisher": "지학사", "author": "지학사 편집부", "isbn": "978-89-408-1239-0",
            "description": "중학교 2학년 사회 탐구 교재", "edition": "2024년판",
            "quantity": 22, "min_quantity": 5, "price": 11000, "is_active": True
        },
        {
            "name": "고등 물리 기초", "subject": "물리", "grade": "고1", 
            "publisher": "미래엔", "author": "미래엔 편집부", "isbn": "978-89-408-1240-6",
            "description": "고등학교 1학년 물리 기초 교재", "edition": "2024년판",
            "quantity": 10, "min_quantity": 2, "price": 14500, "is_active": True
        },
        {
            "name": "중등 화학 실험", "subject": "화학", "grade": "중3", 
            "publisher": "천재교육", "author": "천재교육 편집부", "isbn": "978-89-408-1241-3",
            "description": "중학교 3학년 화학 실험 교재", "edition": "2024년판",
            "quantity": 12, "min_quantity": 3, "price": 13000, "is_active": True
        },
        {
            "name": "고등 생명과학", "subject": "생물", "grade": "고2", 
            "publisher": "YBM", "author": "YBM 편집부", "isbn": "978-89-408-1242-0",
            "description": "고등학교 2학년 생명과학 교재", "edition": "2024년판",
            "quantity": 8, "min_quantity": 2, "price": 15500, "is_active": True
        },
        {
            "name": "중등 지구과학", "subject": "지구과학", "grade": "중2", 
            "publisher": "비상교육", "author": "비상교육 편집부", "isbn": "978-89-408-1243-7",
            "description": "중학교 2학년 지구과학 교재", "edition": "2024년판",
            "quantity": 14, "min_quantity": 4, "price": 12000, "is_active": True
        }
    ]
    
    db = next(get_session())
    
    try:
        # 기존 교재 수 확인
        existing_count = len(db.exec(select(Material)).all())
        log_message(f"기존 교재 수: {existing_count}권")
        
        if existing_count >= 10:
            log_message("이미 10권 이상의 교재가 있습니다.")
            return
        
        to_add = 10 - existing_count
        log_message(f"추가할 교재 수: {to_add}권")
        
        materials_to_add = []
        
        for i, material_data in enumerate(sample_materials[:to_add]):
            # 기존 교재 확인
            existing_material = db.exec(select(Material).where(Material.name == material_data["name"])).first()
            if existing_material:
                log_message(f"이미 존재하는 교재: {material_data['name']}")
                continue
                
            material = Material(**material_data)
            materials_to_add.append(material)
            log_message(f"교재 추가: {material_data['name']} - {material_data['subject']}")
        
        # 일괄 추가
        if materials_to_add:
            db.add_all(materials_to_add)
            db.commit()
            log_message(f"✅ {len(materials_to_add)}권의 샘플 교재가 성공적으로 추가되었습니다!")
        else:
            log_message("추가할 교재가 없습니다.")
        
        # 최종 확인
        final_count = len(db.exec(select(Material)).all())
        log_message(f"총 교재 수: {final_count}권")
        
        # 추가된 교재 목록 출력
        all_materials = db.exec(select(Material)).all()
        log_message("=== 현재 DB의 모든 교재 ===")
        for material in all_materials:
            log_message(f"- {material.name} ({material.subject}, {material.grade})")
        
    except Exception as e:
        log_message(f"❌ 오류 발생: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
        log_message("=== 교재 샘플 데이터 추가 완료 ===")

if __name__ == "__main__":
    add_sample_materials() 
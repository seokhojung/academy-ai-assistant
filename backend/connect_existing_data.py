#!/usr/bin/env python3
"""
Phase 1: 기존 데이터베이스 연결 스크립트
- 강사-강의 연결 (과목별 매칭)
- 교재-강의 연결 (과목+학년별 매칭)
"""

import os
import sys
from datetime import datetime
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.lecture import Lecture
from app.models.teacher import Teacher
from app.models.material import Material

def connect_teachers_to_lectures():
    """과목별로 강사와 강의 연결"""
    print("🔗 강사-강의 연결 시작...")
    
    session = next(get_session())
    
    try:
        # 모든 강의 조회
        lectures = session.exec(select(Lecture)).all()
        print(f"📚 총 강의 수: {len(lectures)}")
        
        # 모든 교사 조회
        teachers = session.exec(select(Teacher)).all()
        print(f"👨‍🏫 총 교사 수: {len(teachers)}")
        
        # 과목별 교사 매핑
        subject_teacher_map = {}
        for teacher in teachers:
            if teacher.subject:
                subject_teacher_map[teacher.subject] = teacher.id
                print(f"  📝 {teacher.subject}: {teacher.name} (ID: {teacher.id})")
        
        # 강의별 교사 연결
        connected_count = 0
        for lecture in lectures:
            if lecture.teacher_id is None and lecture.subject in subject_teacher_map:
                lecture.teacher_id = subject_teacher_map[lecture.subject]
                lecture.updated_at = datetime.utcnow()
                connected_count += 1
                print(f"  ✅ {lecture.title} → {lecture.subject} 교사 연결")
        
        session.commit()
        print(f"🎉 강사-강의 연결 완료: {connected_count}개 강의 연결됨")
        
        return True
        
    except Exception as e:
        print(f"❌ 강사-강의 연결 실패: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def connect_materials_to_lectures():
    """과목+학년별로 교재와 강의 연결"""
    print("🔗 교재-강의 연결 시작...")
    
    session = next(get_session())
    
    try:
        # 모든 강의 조회
        lectures = session.exec(select(Lecture)).all()
        print(f"📚 총 강의 수: {len(lectures)}")
        
        # 모든 교재 조회
        materials = session.exec(select(Material)).all()
        print(f"📖 총 교재 수: {len(materials)}")
        
        # 과목+학년별 교재 매핑
        subject_grade_material_map = {}
        for material in materials:
            if material.subject and material.grade:
                key = f"{material.subject}_{material.grade}"
                subject_grade_material_map[key] = material.id
                print(f"  📝 {material.subject} {material.grade}: {material.name} (ID: {material.id})")
        
        # 강의별 교재 연결
        connected_count = 0
        for lecture in lectures:
            if lecture.material_id is None:
                key = f"{lecture.subject}_{lecture.grade}"
                if key in subject_grade_material_map:
                    lecture.material_id = subject_grade_material_map[key]
                    lecture.updated_at = datetime.utcnow()
                    connected_count += 1
                    print(f"  ✅ {lecture.title} → {lecture.subject} {lecture.grade} 교재 연결")
        
        session.commit()
        print(f"🎉 교재-강의 연결 완료: {connected_count}개 강의 연결됨")
        
        return True
        
    except Exception as e:
        print(f"❌ 교재-강의 연결 실패: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def verify_connections():
    """연결 결과 검증"""
    print("🔍 연결 결과 검증...")
    
    session = next(get_session())
    
    try:
        # 연결된 강의 통계
        lectures = session.exec(select(Lecture)).all()
        total_lectures = len(lectures)
        connected_teacher = sum(1 for l in lectures if l.teacher_id is not None)
        connected_material = sum(1 for l in lectures if l.material_id is not None)
        
        print(f"📊 연결 통계:")
        print(f"  총 강의: {total_lectures}개")
        print(f"  교사 연결: {connected_teacher}개 ({connected_teacher/total_lectures*100:.1f}%)")
        print(f"  교재 연결: {connected_material}개 ({connected_material/total_lectures*100:.1f}%)")
        
        # 연결된 강의 상세 정보
        print(f"\n📋 연결된 강의 상세:")
        for lecture in lectures:
            teacher_name = "연결 안됨"
            material_name = "연결 안됨"
            
            if lecture.teacher_id:
                teacher = session.exec(select(Teacher).where(Teacher.id == lecture.teacher_id)).first()
                if teacher:
                    teacher_name = teacher.name
            
            if lecture.material_id:
                material = session.exec(select(Material).where(Material.id == lecture.material_id)).first()
                if material:
                    material_name = material.name
            
            print(f"  {lecture.title}: {teacher_name} / {material_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 검증 실패: {e}")
        return False
    finally:
        session.close()

def main():
    """메인 실행 함수"""
    print("🚀 Phase 1: 기존 데이터 연결 시작")
    print("=" * 50)
    
    # 1. 강사-강의 연결
    if not connect_teachers_to_lectures():
        print("❌ Phase 1 실패: 강사-강의 연결 실패")
        return False
    
    print()
    
    # 2. 교재-강의 연결
    if not connect_materials_to_lectures():
        print("❌ Phase 1 실패: 교재-강의 연결 실패")
        return False
    
    print()
    
    # 3. 연결 결과 검증
    if not verify_connections():
        print("❌ Phase 1 실패: 검증 실패")
        return False
    
    print()
    print("🎉 Phase 1 완료: 기존 데이터 연결 성공!")
    print("📈 이제 통계가 실제 데이터를 반영합니다.")
    
    return True

if __name__ == "__main__":
    # 현재 디렉토리를 backend로 변경
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Python 경로에 현재 디렉토리 추가
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    success = main()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
누락된 연결 추가 스크립트
- 교재 연결이 없는 강의들에 적절한 교재 연결
- 교사 연결이 없는 강의들에 적절한 교사 연결
"""

import os
import sys
from datetime import datetime
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.lecture import Lecture
from app.models.teacher import Teacher
from app.models.material import Material

def fix_missing_connections():
    """누락된 연결들을 수정"""
    print("🔧 누락된 연결 수정 시작...")
    
    session = next(get_session())
    
    try:
        # 모든 강의 조회
        lectures = session.exec(select(Lecture)).all()
        print(f"📚 총 강의 수: {len(lectures)}")
        
        # 모든 교사와 교재 조회
        teachers = session.exec(select(Teacher)).all()
        materials = session.exec(select(Material)).all()
        
        # 과목별 교사 매핑
        subject_teacher_map = {t.subject: t.id for t in teachers if t.subject}
        
        # 과목+학년별 교재 매핑
        subject_grade_material_map = {}
        for material in materials:
            if material.subject and material.grade:
                key = f"{material.subject}_{material.grade}"
                subject_grade_material_map[key] = material.id
        
        # 연결 수정
        fixed_count = 0
        
        for lecture in lectures:
            fixed = False
            
            # 1. 교사 연결이 없는 경우
            if lecture.teacher_id is None and lecture.subject in subject_teacher_map:
                lecture.teacher_id = subject_teacher_map[lecture.subject]
                lecture.updated_at = datetime.utcnow()
                print(f"  ✅ {lecture.title}: 교사 연결 추가")
                fixed = True
            
            # 2. 교재 연결이 없는 경우
            if lecture.material_id is None:
                key = f"{lecture.subject}_{lecture.grade}"
                if key in subject_grade_material_map:
                    lecture.material_id = subject_grade_material_map[key]
                    lecture.updated_at = datetime.utcnow()
                    print(f"  ✅ {lecture.title}: 교재 연결 추가")
                    fixed = True
            
            if fixed:
                fixed_count += 1
        
        session.commit()
        print(f"🎉 연결 수정 완료: {fixed_count}개 강의 수정됨")
        
        return True
        
    except Exception as e:
        print(f"❌ 연결 수정 실패: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def verify_final_connections():
    """최종 연결 상태 검증"""
    print("🔍 최종 연결 상태 검증...")
    
    session = next(get_session())
    
    try:
        lectures = session.exec(select(Lecture)).all()
        total_lectures = len(lectures)
        connected_teacher = sum(1 for l in lectures if l.teacher_id is not None)
        connected_material = sum(1 for l in lectures if l.material_id is not None)
        
        print(f"📊 최종 연결 통계:")
        print(f"  총 강의: {total_lectures}개")
        print(f"  교사 연결: {connected_teacher}개 ({connected_teacher/total_lectures*100:.1f}%)")
        print(f"  교재 연결: {connected_material}개 ({connected_material/total_lectures*100:.1f}%)")
        
        print(f"\n📋 최종 연결 상태:")
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
            
            status = "✅ 완전 연결" if lecture.teacher_id and lecture.material_id else "⚠️ 부분 연결" if lecture.teacher_id or lecture.material_id else "❌ 연결 없음"
            print(f"  {status} {lecture.title}: {teacher_name} / {material_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 검증 실패: {e}")
        return False
    finally:
        session.close()

def main():
    """메인 실행 함수"""
    print("🚀 누락된 연결 수정 시작")
    print("=" * 50)
    
    # 1. 누락된 연결 수정
    if not fix_missing_connections():
        print("❌ 연결 수정 실패")
        return False
    
    print()
    
    # 2. 최종 검증
    if not verify_final_connections():
        print("❌ 최종 검증 실패")
        return False
    
    print()
    print("🎉 Phase 1 완료: 모든 연결 수정 완료!")
    print("📈 이제 통계가 실제 데이터를 반영합니다.")
    
    return True

if __name__ == "__main__":
    # 현재 디렉토리를 backend로 변경
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Python 경로에 현재 디렉토리 추가
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    success = main()
    sys.exit(0 if success else 1) 
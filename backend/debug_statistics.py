#!/usr/bin/env python3
"""
통계 서비스 디버깅 스크립트
"""

import os
import sys
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.lecture import Lecture
from app.models.teacher import Teacher
from app.models.material import Material

def debug_teacher_statistics():
    """강사 통계 디버깅"""
    print("🔍 강사 통계 디버깅...")
    
    session = next(get_session())
    
    try:
        # 1. 전체 강사 수
        total_teachers = session.exec(select(Teacher)).all()
        print(f"📊 전체 강사 수: {len(total_teachers)}")
        
        # 2. 활성 강사 수
        active_teachers = session.exec(
            select(Teacher).where(Teacher.is_active == True)
        ).all()
        print(f"📊 활성 강사 수: {len(active_teachers)}")
        
        # 3. 각 강사별 강의 확인
        print("\n👨‍🏫 강사별 강의 현황:")
        for teacher in active_teachers:
            teacher_lectures = session.exec(
                select(Lecture).where(Lecture.teacher_id == teacher.id)
            ).all()
            
            lecture_count = len(teacher_lectures)
            total_students = sum(lecture.current_students for lecture in teacher_lectures)
            
            print(f"  {teacher.name} ({teacher.subject}):")
            print(f"    - 강의 수: {lecture_count}개")
            print(f"    - 총 수강생: {total_students}명")
            
            for lecture in teacher_lectures:
                print(f"      * {lecture.title}: {lecture.current_students}명")
        
        # 4. 과목별 강사 분포 확인
        print("\n📚 과목별 강사 분포:")
        subject_teacher_map = {}
        for teacher in active_teachers:
            teacher_lectures = session.exec(
                select(Lecture.subject).where(Lecture.teacher_id == teacher.id)
            ).all()
            
            for subject_lecture in teacher_lectures:
                if subject_lecture.subject not in subject_teacher_map:
                    subject_teacher_map[subject_lecture.subject] = set()
                subject_teacher_map[subject_lecture.subject].add(teacher.id)
        
        for subject, teacher_ids in subject_teacher_map.items():
            print(f"  {subject}: {len(teacher_ids)}명")
        
        return True
        
    except Exception as e:
        print(f"❌ 디버깅 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

def debug_material_statistics():
    """교재 통계 디버깅"""
    print("\n🔍 교재 통계 디버깅...")
    
    session = next(get_session())
    
    try:
        # 1. 전체 교재 수
        total_materials = session.exec(select(Material)).all()
        print(f"📊 전체 교재 수: {len(total_materials)}")
        
        # 2. 활성 교재 수
        active_materials = session.exec(
            select(Material).where(Material.is_active == True)
        ).all()
        print(f"📊 활성 교재 수: {len(active_materials)}")
        
        # 3. 각 교재별 사용 현황
        print("\n📖 교재별 사용 현황:")
        for material in active_materials:
            material_lectures = session.exec(
                select(Lecture).where(Lecture.material_id == material.id)
            ).all()
            
            lecture_count = len(material_lectures)
            total_students = sum(lecture.current_students for lecture in material_lectures)
            
            print(f"  {material.name} ({material.subject} {material.grade}):")
            print(f"    - 사용 강의 수: {lecture_count}개")
            print(f"    - 총 수강생: {total_students}명")
            
            for lecture in material_lectures:
                print(f"      * {lecture.title}: {lecture.current_students}명")
        
        return True
        
    except Exception as e:
        print(f"❌ 디버깅 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

def main():
    """메인 실행 함수"""
    print("🚀 통계 서비스 디버깅 시작")
    print("=" * 50)
    
    # 1. 강사 통계 디버깅
    if not debug_teacher_statistics():
        print("❌ 강사 통계 디버깅 실패")
        return False
    
    # 2. 교재 통계 디버깅
    if not debug_material_statistics():
        print("❌ 교재 통계 디버깅 실패")
        return False
    
    print("\n🎉 디버깅 완료!")
    return True

if __name__ == "__main__":
    # 현재 디렉토리를 backend로 변경
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Python 경로에 현재 디렉토리 추가
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    success = main()
    sys.exit(0 if success else 1) 
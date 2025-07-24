#!/usr/bin/env python3
"""
강사 통계를 위한 연결 데이터 추가 스크립트
"""

import os
import sys
from datetime import datetime, timedelta
from sqlmodel import SQLModel, create_engine, Session, select
from app.models.teacher import Teacher
from app.models.student import Student
from app.models.lecture import Lecture
from app.models.material import Material

def fix_teacher_statistics_data():
    """강사 통계를 위한 연결 데이터 추가"""
    print("=== 강사 통계를 위한 연결 데이터 추가 시작 ===")
    
    # DB URL 설정
    db_url = "sqlite:///./academy.db"
    print(f"[DEBUG] DB URL: {db_url}")
    
    # 엔진 생성
    engine = create_engine(db_url, echo=True)
    
    with Session(engine) as session:
        try:
            # 1. 강의-강사 연결 (teacher_id 설정)
            print("\n📚 1단계: 강의-강사 연결...")
            lectures = session.exec(select(Lecture)).all()
            teachers = session.exec(select(Teacher)).all()
            
            # 과목별로 강사 매칭
            subject_teacher_map = {}
            for teacher in teachers:
                subject_teacher_map[teacher.subject] = teacher.id
            
            connected_lectures = 0
            for lecture in lectures:
                if lecture.subject in subject_teacher_map:
                    lecture.teacher_id = subject_teacher_map[lecture.subject]
                    connected_lectures += 1
                    print(f"✅ {lecture.title} -> {lecture.subject} 강사 연결")
            
            print(f"📊 강의-강사 연결 완료: {connected_lectures}/{len(lectures)}개")
            
            # 2. 강의-교재 연결 (material_id 설정)
            print("\n📖 2단계: 강의-교재 연결...")
            materials = session.exec(select(Material)).all()
            
            # 과목+학년별로 교재 매칭
            subject_grade_material_map = {}
            for material in materials:
                key = f"{material.subject}_{material.grade}"
                subject_grade_material_map[key] = material.id
            
            connected_materials = 0
            for lecture in lectures:
                key = f"{lecture.subject}_{lecture.grade}"
                if key in subject_grade_material_map:
                    lecture.material_id = subject_grade_material_map[key]
                    connected_materials += 1
                    print(f"✅ {lecture.title} -> {key} 교재 연결")
            
            print(f"📊 강의-교재 연결 완료: {connected_materials}/{len(lectures)}개")
            
            # 3. 강의 정보 업데이트 (통계용 필드)
            print("\n📈 3단계: 강의 통계 정보 업데이트...")
            for lecture in lectures:
                # 강의 난이도 설정
                if "심화" in lecture.title:
                    lecture.difficulty_level = "고급"
                elif "기초" in lecture.title:
                    lecture.difficulty_level = "초급"
                else:
                    lecture.difficulty_level = "중급"
                
                # 강의 시간 설정
                lecture.class_duration = 120  # 2시간
                lecture.total_sessions = 20   # 총 20회
                lecture.completed_sessions = 10  # 10회 완료
                
                # 만족도 및 평점 설정
                lecture.student_satisfaction = 4.2 + (lecture.current_students / lecture.max_students) * 0.8
                lecture.teacher_rating = 4.5 + (lecture.current_students / lecture.max_students) * 0.5
                
                print(f"✅ {lecture.title} 통계 정보 업데이트")
            
            # 4. 강사 정보 업데이트 (통계용 필드)
            print("\n👨‍🏫 4단계: 강사 통계 정보 업데이트...")
            for teacher in teachers:
                # 경력 연수 설정
                teacher.experience_years = 3 + (teacher.id % 7)  # 3-9년
                
                # 교육 수준 설정
                if teacher.id % 3 == 0:
                    teacher.education_level = "master"
                elif teacher.id % 3 == 1:
                    teacher.education_level = "phd"
                else:
                    teacher.education_level = "bachelor"
                
                # 전문 분야 설정
                teacher.specialization = f"{teacher.subject} 전문가"
                
                # 고용일 설정
                teacher.hire_date = datetime.now() - timedelta(days=365 * teacher.experience_years)
                
                # 계약 형태 설정
                if teacher.id % 2 == 0:
                    teacher.contract_type = "full_time"
                else:
                    teacher.contract_type = "part_time"
                
                # 최대 강의 수 설정
                teacher.max_lectures = 8 if teacher.contract_type == "full_time" else 5
                
                # 평점 설정
                teacher.rating = 4.0 + (teacher.id % 10) * 0.1  # 4.0-4.9
                
                # 총 강의 시간 설정
                teacher.total_teaching_hours = teacher.experience_years * 200  # 연간 200시간
                
                # 자격증 설정
                teacher.certification = f"[\"{teacher.subject}교사자격증\", \"교육학석사\"]"
                
                print(f"✅ {teacher.name} 통계 정보 업데이트")
            
            # 5. 변경사항 저장
            session.commit()
            print("\n💾 모든 변경사항 저장 완료")
            
            # 6. 결과 검증
            print("\n🔍 6단계: 연결 결과 검증...")
            
            # 강의-강사 연결 확인
            lectures_with_teacher = session.exec(
                select(Lecture).where(Lecture.teacher_id.is_not(None))
            ).all()
            print(f"📊 강사 연결된 강의: {len(lectures_with_teacher)}/{len(lectures)}개")
            
            # 강의-교재 연결 확인
            lectures_with_material = session.exec(
                select(Lecture).where(Lecture.material_id.is_not(None))
            ).all()
            print(f"📊 교재 연결된 강의: {len(lectures_with_material)}/{len(lectures)}개")
            
            # 강사별 강의 수 확인
            for teacher in teachers:
                teacher_lectures = session.exec(
                    select(Lecture).where(Lecture.teacher_id == teacher.id)
                ).all()
                print(f"👨‍🏫 {teacher.name}: {len(teacher_lectures)}개 강의")
            
            print("\n✅ 강사 통계를 위한 연결 데이터 추가 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return False

if __name__ == "__main__":
    fix_teacher_statistics_data() 
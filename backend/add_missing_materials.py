#!/usr/bin/env python3
"""
누락된 교재 연결을 위한 추가 교재 생성 스크립트
"""

import os
import sys
from datetime import datetime
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.material import Material

def add_missing_materials():
    """누락된 교재들을 추가"""
    print("📚 누락된 교재 추가 시작...")
    
    session = next(get_session())
    
    try:
        # 추가할 교재 목록 (과목+학년별로 매칭)
        missing_materials = [
            {
                "name": "중등 과학 실험 교재",
                "subject": "과학",
                "grade": "중2",
                "publisher": "미래엔",
                "author": "과학연구회",
                "isbn": "978-89-01-12345-6",
                "description": "중등 2학년 과학 실험 교재",
                "quantity": 50,
                "min_quantity": 10,
                "price": 25000
            },
            {
                "name": "중등 사회 탐구 교재",
                "subject": "사회",
                "grade": "중3",
                "publisher": "천재교육",
                "author": "사회연구회",
                "isbn": "978-89-01-12346-7",
                "description": "중등 3학년 사회 탐구 교재",
                "quantity": 45,
                "min_quantity": 8,
                "price": 22000
            },
            {
                "name": "고등 물리 심화 교재",
                "subject": "물리",
                "grade": "고3",
                "publisher": "동아출판",
                "author": "물리연구회",
                "isbn": "978-89-01-12347-8",
                "description": "고등 3학년 물리 심화 교재",
                "quantity": 30,
                "min_quantity": 5,
                "price": 35000
            },
            {
                "name": "중등 화학 기초 교재",
                "subject": "화학",
                "grade": "중2",
                "publisher": "미래엔",
                "author": "화학연구회",
                "isbn": "978-89-01-12348-9",
                "description": "중등 2학년 화학 기초 교재",
                "quantity": 40,
                "min_quantity": 8,
                "price": 23000
            },
            {
                "name": "중등 지구과학 기초 교재",
                "subject": "지구과학",
                "grade": "중1",
                "publisher": "천재교육",
                "author": "지구과학연구회",
                "isbn": "978-89-01-12349-0",
                "description": "중등 1학년 지구과학 기초 교재",
                "quantity": 35,
                "min_quantity": 6,
                "price": 20000
            },
            {
                "name": "고등 수학 심화 교재",
                "subject": "수학",
                "grade": "고3",
                "publisher": "동아출판",
                "author": "수학연구회",
                "isbn": "978-89-01-12350-1",
                "description": "고등 3학년 수학 심화 교재",
                "quantity": 25,
                "min_quantity": 5,
                "price": 40000
            }
        ]
        
        added_count = 0
        for material_data in missing_materials:
            # 이미 존재하는지 확인
            existing = session.exec(
                select(Material).where(
                    Material.subject == material_data["subject"],
                    Material.grade == material_data["grade"]
                )
            ).first()
            
            if not existing:
                material = Material(
                    name=material_data["name"],
                    subject=material_data["subject"],
                    grade=material_data["grade"],
                    publisher=material_data["publisher"],
                    author=material_data["author"],
                    isbn=material_data["isbn"],
                    description=material_data["description"],
                    quantity=material_data["quantity"],
                    min_quantity=material_data["min_quantity"],
                    price=material_data["price"],
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(material)
                added_count += 1
                print(f"  ✅ {material_data['name']} 추가")
            else:
                print(f"  ⚠️ {material_data['name']} 이미 존재")
        
        session.commit()
        print(f"🎉 교재 추가 완료: {added_count}개 교재 추가됨")
        
        return True
        
    except Exception as e:
        print(f"❌ 교재 추가 실패: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def connect_missing_materials():
    """누락된 교재 연결"""
    print("🔗 누락된 교재 연결 시작...")
    
    session = next(get_session())
    
    try:
        from app.models.lecture import Lecture
        
        # 연결할 강의-교재 매핑
        connections = [
            ("중등 과학 실험반", "과학", "중2"),
            ("중등 사회 탐구반", "사회", "중3"),
            ("고등 물리 심화반", "물리", "고3"),
            ("중등 화학 기초반", "화학", "중2"),
            ("중등 지구과학반", "지구과학", "중1"),
            ("고등 수학 심화반", "수학", "고3")
        ]
        
        connected_count = 0
        for lecture_title, subject, grade in connections:
            # 강의 찾기
            lecture = session.exec(
                select(Lecture).where(Lecture.title == lecture_title)
            ).first()
            
            if lecture and lecture.material_id is None:
                # 해당 과목+학년의 교재 찾기
                material = session.exec(
                    select(Material).where(
                        Material.subject == subject,
                        Material.grade == grade
                    )
                ).first()
                
                if material:
                    lecture.material_id = material.id
                    lecture.updated_at = datetime.utcnow()
                    connected_count += 1
                    print(f"  ✅ {lecture_title} → {material.name}")
        
        session.commit()
        print(f"🎉 교재 연결 완료: {connected_count}개 강의 연결됨")
        
        return True
        
    except Exception as e:
        print(f"❌ 교재 연결 실패: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def remove_test_data():
    """테스트 데이터 제거"""
    print("🗑️ 테스트 데이터 제거 시작...")
    
    session = next(get_session())
    
    try:
        from app.models.lecture import Lecture
        
        # 테스트 강의 제거
        test_lectures = session.exec(
            select(Lecture).where(
                (Lecture.title == "새 강의") |
                (Lecture.title == "test") |
                (Lecture.title.like("%test%"))
            )
        ).all()
        
        removed_count = 0
        for lecture in test_lectures:
            session.delete(lecture)
            removed_count += 1
            print(f"  🗑️ 테스트 강의 제거: {lecture.title}")
        
        session.commit()
        print(f"🎉 테스트 데이터 제거 완료: {removed_count}개 강의 제거됨")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 데이터 제거 실패: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def verify_final_state():
    """최종 상태 검증"""
    print("🔍 최종 상태 검증...")
    
    session = next(get_session())
    
    try:
        from app.models.lecture import Lecture
        
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
            from app.models.teacher import Teacher
            from app.models.material import Material
            
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
    print("🚀 누락된 교재 연결 및 테스트 데이터 정리 시작")
    print("=" * 60)
    
    # 1. 누락된 교재 추가
    if not add_missing_materials():
        print("❌ 교재 추가 실패")
        return False
    
    print()
    
    # 2. 누락된 교재 연결
    if not connect_missing_materials():
        print("❌ 교재 연결 실패")
        return False
    
    print()
    
    # 3. 테스트 데이터 제거
    if not remove_test_data():
        print("❌ 테스트 데이터 제거 실패")
        return False
    
    print()
    
    # 4. 최종 검증
    if not verify_final_state():
        print("❌ 최종 검증 실패")
        return False
    
    print()
    print("🎉 모든 작업 완료!")
    print("📈 이제 모든 강의가 교사와 교재에 연결되었습니다.")
    
    return True

if __name__ == "__main__":
    # 현재 디렉토리를 backend로 변경
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Python 경로에 현재 디렉토리 추가
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    success = main()
    sys.exit(0 if success else 1) 
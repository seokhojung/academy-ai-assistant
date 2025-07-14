#!/usr/bin/env python3
"""
학생 샘플 데이터 추가 스크립트
50명의 한국 학생 데이터를 생성합니다.
"""

import random
from datetime import datetime, timedelta
from sqlmodel import select, desc
from app.core.database import get_session
from app.models.student import Student

# 한국 이름 데이터
KOREAN_NAMES = [
    "김민준", "이서준", "박도윤", "최예준", "정시우", "강하준", "조주원", "윤도현", "장동현", "임재현",
    "한지호", "오서진", "신민재", "권우진", "황준서", "안현우", "송민석", "류지훈", "백준혁", "남도현",
    "김서연", "이지은", "박수빈", "최예은", "정하은", "강지민", "조서현", "윤지원", "장예진", "임민지",
    "한소연", "오지현", "신예원", "권수민", "황은지", "안지영", "송민아", "류예린", "백하나", "남서영",
    "김준호", "이현우", "박민수", "최지훈", "정도현", "강재현", "조시우", "윤하준", "장주원", "임도현"
]

# 이메일 도메인
EMAIL_DOMAINS = ["gmail.com", "naver.com", "daum.net", "hanmail.net", "hotmail.com"]

# 학년 목록
GRADES = ["고등학교 1학년", "고등학교 2학년", "고등학교 3학년"]

def generate_phone():
    """전화번호 생성"""
    return f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def generate_email(name):
    """이메일 생성"""
    domain = random.choice(EMAIL_DOMAINS)
    number = random.randint(1, 999)
    return f"{name.lower()}{number}@{domain}"

def generate_enrollment_date():
    """등록일 생성 (최근 2년 내)"""
    days_ago = random.randint(1, 730)  # 2년 내
    return datetime.now() - timedelta(days=days_ago)

def generate_tuition_fee():
    """수강료 생성 (20만원 ~ 50만원)"""
    return random.randint(200000, 500000)

def generate_tuition_due_date():
    """수강료 납부일 생성 (다음 달 1~15일)"""
    next_month = datetime.now().replace(day=1) + timedelta(days=32)
    next_month = next_month.replace(day=1)
    due_day = random.randint(1, 15)
    return next_month.replace(day=due_day)

def create_sample_students():
    """샘플 학생 데이터 생성"""
    print("샘플 학생 데이터를 생성합니다...")
    
    # 기존 학생 수 확인
    with next(get_session()) as db:
        existing_count = len(db.exec(select(Student)).all())
        print(f"현재 등록된 학생 수: {existing_count}명")
        
        # 50명까지 추가
        target_count = 50
        students_to_add = target_count - existing_count
        
        if students_to_add <= 0:
            print("이미 50명 이상의 학생이 등록되어 있습니다.")
            return
        
        print(f"{students_to_add}명의 학생을 추가합니다...")
        
        # 사용할 이름 목록 (중복 방지)
        available_names = KOREAN_NAMES.copy()
        random.shuffle(available_names)
        
        for i in range(students_to_add):
            if i >= len(available_names):
                # 이름이 부족하면 숫자 추가
                base_name = random.choice(KOREAN_NAMES)
                name = f"{base_name}{i+1}"
            else:
                name = available_names[i]
            
            # 중복되지 않는 이메일 생성
            email = generate_email(name)
            while db.exec(select(Student).where(Student.email == email)).first():
                email = generate_email(name)
            
            student = Student(
                name=name,
                email=email,
                phone=generate_phone(),
                grade=random.choice(GRADES),
                tuition_fee=generate_tuition_fee(),
                tuition_due_date=generate_tuition_due_date(),
                is_active=True,
                created_at=generate_enrollment_date(),
                updated_at=datetime.now()
            )
            
            db.add(student)
            
            if (i + 1) % 10 == 0:
                print(f"진행률: {i + 1}/{students_to_add}")
        
        db.commit()
        
        # 최종 결과 확인
        final_count = len(db.exec(select(Student)).all())
        print(f"✅ 완료! 총 {final_count}명의 학생이 등록되었습니다.")
        
        # 최근 추가된 학생 5명 출력
        recent_students = db.exec(
            select(Student)
            .order_by(desc(Student.created_at))
            .limit(5)
        ).all()
        
        print("\n최근 추가된 학생 5명:")
        for i, student in enumerate(recent_students, 1):
            print(f"{i}. {student.name} ({student.email}) - {student.grade}")

if __name__ == "__main__":
    create_sample_students() 
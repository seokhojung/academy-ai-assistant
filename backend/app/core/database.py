from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import inspect
from .config import settings

# Create database engine
engine = create_engine(
    settings.get_database_url,
    echo=settings.debug,
    # PostgreSQL용 연결 설정
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"check_same_thread": False} if "sqlite" in settings.get_database_url else {}
)


def create_db_and_tables():
    """Create database tables (기존 데이터 유지)"""
    try:
        # 기존 테이블 확인
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            # 테이블이 없을 때만 생성
            SQLModel.metadata.create_all(engine)
            print("✅ 새로운 테이블 생성됨")
            
            # 프로덕션 환경에서만 샘플 데이터 추가
            if settings.environment == "production":
                print("🔄 프로덕션 환경: 샘플 데이터 추가 중...")
                add_sample_data_if_empty()
        else:
            print(f"✅ 기존 테이블 유지됨: {existing_tables}")
            
    except Exception as e:
        print(f"❌ 테이블 생성 중 오류: {e}")
        # 오류 발생 시에도 테이블 생성 시도
        SQLModel.metadata.create_all(engine)


def add_sample_data_if_empty():
    """테이블이 비어있을 때만 샘플 데이터 추가"""
    try:
        with Session(engine) as session:
            # 학생 수 확인
            from app.models.student import Student
            student_count = session.query(Student).count()
            
            if student_count == 0:
                print("📊 빈 데이터베이스 감지: 샘플 데이터 추가 시작")
                # 샘플 데이터 추가 로직
                add_sample_students(session)
                add_sample_teachers(session)
                add_sample_materials(session)
                add_sample_lectures(session)
                print("✅ 샘플 데이터 추가 완료")
            else:
                print(f"✅ 기존 데이터 유지: 학생 {student_count}명")
                
    except Exception as e:
        print(f"❌ 샘플 데이터 추가 중 오류: {e}")


def add_sample_students(session: Session):
    """샘플 학생 데이터 추가"""
    from app.models.student import Student
    
    sample_students = [
        {"name": "김철수", "grade": "고1", "email": "kim@academy.com", "phone": "010-1234-5678"},
        {"name": "이영희", "grade": "고2", "email": "lee@academy.com", "phone": "010-2345-6789"},
        {"name": "박민수", "grade": "고3", "email": "park@academy.com", "phone": "010-3456-7890"},
    ]
    
    for student_data in sample_students:
        student = Student(**student_data)
        session.add(student)
    
    session.commit()
    print(f"✅ {len(sample_students)}명의 샘플 학생 추가됨")


def add_sample_teachers(session: Session):
    """샘플 강사 데이터 추가"""
    from app.models.teacher import Teacher
    
    sample_teachers = [
        {"name": "김수학", "subject": "수학", "email": "math@academy.com", "phone": "010-1111-2222"},
        {"name": "이영어", "subject": "영어", "email": "english@academy.com", "phone": "010-3333-4444"},
        {"name": "박과학", "subject": "과학", "email": "science@academy.com", "phone": "010-5555-6666"},
    ]
    
    for teacher_data in sample_teachers:
        teacher = Teacher(**teacher_data)
        session.add(teacher)
    
    session.commit()
    print(f"✅ {len(sample_teachers)}명의 샘플 강사 추가됨")


def add_sample_materials(session: Session):
    """샘플 교재 데이터 추가"""
    from app.models.material import Material
    
    sample_materials = [
        {"name": "중등 수학 1", "subject": "수학", "grade": "중1"},
        {"name": "고등 영어 독해", "subject": "영어", "grade": "고1"},
        {"name": "중등 과학 실험", "subject": "과학", "grade": "중3"},
    ]
    
    for material_data in sample_materials:
        material = Material(**material_data)
        session.add(material)
    
    session.commit()
    print(f"✅ {len(sample_materials)}개의 샘플 교재 추가됨")


def add_sample_lectures(session: Session):
    """샘플 강의 데이터 추가"""
    from app.models.lecture import Lecture
    
    sample_lectures = [
        {"title": "고1 수학 기초", "subject": "수학", "grade": "고1", "schedule": "월수금 14:00-16:00"},
        {"title": "고2 영어 독해", "subject": "영어", "grade": "고2", "schedule": "화목 15:00-17:00"},
        {"title": "중3 과학 실험", "subject": "과학", "grade": "중3", "schedule": "토 10:00-12:00"},
    ]
    
    for lecture_data in sample_lectures:
        lecture = Lecture(**lecture_data)
        session.add(lecture)
    
    session.commit()
    print(f"✅ {len(sample_lectures)}개의 샘플 강의 추가됨")


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session 
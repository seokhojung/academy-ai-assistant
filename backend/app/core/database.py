from sqlmodel import SQLModel, create_engine, Session
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
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session 
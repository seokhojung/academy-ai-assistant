from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import create_db_and_tables
import sys
import os

# 로깅 설정 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import setup_logging

# 로깅 초기화
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Academy AI Assistant API",
    description="AI-powered academy management system",
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware with security enhancements
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type", 
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "Cache-Control",
        "Pragma"
    ],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=3600,  # CORS preflight cache (1 hour)
)

# Include routers
from .api.v1 import students
from .api.v1 import ai  # AI 챗봇 라우터 활성화
from .api.v1 import user  # 사용자 컬럼 설정 라우터
from .api.v1 import lectures  # 강의 관리 라우터
from .api.v1 import teachers  # 강사 관리 라우터
from .api.v1 import materials  # 교재 관리 라우터
from .api.v1 import excel_preview  # 엑셀 미리보기 라우터
# from .api.v1 import auth  # 임시 비활성화
# from .api.v1 import files  # 파일 관리 라우터 - 임시 비활성화

app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(user.router, prefix="/api/v1/users", tags=["users"])
app.include_router(lectures.router, prefix="/api/v1/lectures", tags=["lectures"])
app.include_router(teachers.router, prefix="/api/v1/teachers", tags=["teachers"])
app.include_router(materials.router, prefix="/api/v1/materials", tags=["materials"])
app.include_router(excel_preview.router, prefix="/api/v1/excel-preview", tags=["excel-preview"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
# app.include_router(files.router, prefix="/api/v1/files", tags=["files"])  # 임시 비활성화


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    create_db_and_tables()


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Academy AI Assistant API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from .core.database import get_session
    from sqlmodel import Session
    
    try:
        # 데이터베이스 연결 확인
        from sqlalchemy import text
        session = next(get_session())
        session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": "2024-12-19T10:00:00Z",
        "version": "1.0.0",
        "database": db_status,
        "environment": settings.environment
    } 
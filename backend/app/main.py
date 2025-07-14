from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import create_db_and_tables

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
        "Access-Control-Request-Headers"
    ],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=3600,  # CORS preflight cache (1 hour)
)

# Include routers
from .api.v1 import students
from .api.v1 import ai  # AI 챗봇 라우터 활성화
# from .api.v1 import auth  # 임시 비활성화
# from .api.v1 import teachers  # 임시 비활성화
# from .api.v1 import materials  # 임시 비활성화
# from .api.v1 import excel  # 임시 비활성화

app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(teachers.router, prefix="/api/v1/teachers", tags=["teachers"])
# app.include_router(materials.router, prefix="/api/v1/materials", tags=["materials"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
# app.include_router(excel.router, prefix="/api/v1/excel", tags=["excel"])


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
    return {"status": "healthy"} 
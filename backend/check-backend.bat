@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Backend Status Check
echo ========================================

REM 포트 8000 사용 확인
echo Checking port 8000...
netstat -ano | findstr :8000 >nul
if errorlevel 1 (
    echo [ERROR] Backend server is not running on port 8000
    echo.
    echo To start the server, run: start-backend.bat
) else (
    echo [OK] Backend server is running on port 8000
)

REM API 응답 확인
echo.
echo Testing API endpoints...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Health endpoint not responding
) else (
    echo [OK] Health endpoint is responding
)

REM 데이터베이스 연결 확인
echo.
echo Checking database connection...
cd /d %~dp0
if exist venv (
    call venv\Scripts\activate.bat
    python -c "from app.core.database import get_session; from sqlmodel import Session; session = next(get_session()); print('Database connection OK')" 2>nul
    if errorlevel 1 (
        echo [ERROR] Database connection failed
    ) else (
        echo [OK] Database connection successful
    )
) else (
    echo [ERROR] Virtual environment not found
)

REM 의존성 확인
echo.
echo Checking dependencies...
if exist venv (
    call venv\Scripts\activate.bat
    python -c "import fastapi, uvicorn, sqlalchemy, sqlmodel, pydantic" 2>nul
    if errorlevel 1 (
        echo [ERROR] Missing dependencies
        echo Run: pip install -r requirements.txt
    ) else (
        echo [OK] All dependencies are installed
    )
)

echo.
echo ========================================
pause 
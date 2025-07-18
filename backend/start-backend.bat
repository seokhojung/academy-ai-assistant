@echo off
setlocal enabledelayedexpansion

REM 백엔드 폴더로 이동
cd /d %~dp0

echo ========================================
echo Academy AI Assistant - Backend Server
echo ========================================

REM 가상환경 확인 및 생성
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM 가상환경 활성화
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)

REM 의존성 설치 확인
echo Checking dependencies...
python -c "import fastapi, uvicorn, sqlalchemy, sqlmodel" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)

REM 환경변수 설정
set PYTHONPATH=./app
set ENVIRONMENT=development

REM 포트 사용 확인
netstat -ano | findstr :8000 >nul
if not errorlevel 1 (
    echo Port 8000 is already in use. Stopping existing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        taskkill /f /pid %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

echo Starting backend server...
echo Server will be available at: http://localhost:8000
echo API documentation: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

REM 서버 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info 
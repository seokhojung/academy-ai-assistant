@echo off
echo Starting Academy AI Assistant Backend...
echo.

cd backend

REM 가상환경 활성화
call venv\Scripts\activate

REM 백엔드 서버 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause 
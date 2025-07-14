@echo off
REM backend 폴더에서 실행해야 함
cd /d %~dp0

REM 가상환경이 없으면 생성
if not exist venv (
    python -m venv venv
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 패키지 설치 (최초 1회만 필요, 필요시 주석 해제)
REM pip install -r requirements.txt

REM 환경변수 설정 (항상 포함)
set PYTHONPATH=./app

REM 서버 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 
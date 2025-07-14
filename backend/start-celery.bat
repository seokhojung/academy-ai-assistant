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

REM 환경변수 설정
set PYTHONPATH=./app

REM Redis 서버가 실행 중인지 확인 (Windows에서는 별도 설치 필요)
echo Redis 서버가 실행 중인지 확인하세요.
echo Windows에서 Redis 설치: https://github.com/microsoftarchive/redis/releases

REM Celery 워커 실행
python -m celery -A app.workers.celery_app worker --loglevel=info --pool=solo 
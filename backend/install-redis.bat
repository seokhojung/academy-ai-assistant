@echo off
echo Redis 설치 및 실행 스크립트
echo ================================

REM Redis 설치 디렉토리
set REDIS_DIR=C:\Redis
set REDIS_VERSION=5.0.14.1

echo 1. Redis 설치 디렉토리 생성...
if not exist "%REDIS_DIR%" mkdir "%REDIS_DIR%"

echo 2. Redis 다운로드 중...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/microsoftarchive/redis/releases/download/win-%REDIS_VERSION%/Redis-x64-%REDIS_VERSION%.msi' -OutFile '%REDIS_DIR%\Redis-x64-%REDIS_VERSION%.msi'}"

echo 3. Redis 설치 중...
msiexec /i "%REDIS_DIR%\Redis-x64-%REDIS_VERSION%.msi" /quiet

echo 4. Redis 서비스 시작...
net start Redis

echo 5. Redis 연결 테스트...
redis-cli ping

echo.
echo Redis 설치 및 실행이 완료되었습니다!
echo Redis 서버가 localhost:6379에서 실행 중입니다.
echo.
echo 다음 명령어로 Redis 상태를 확인할 수 있습니다:
echo   redis-cli ping
echo   redis-cli info
echo.
echo Redis 서비스를 중지하려면: net stop Redis
echo Redis 서비스를 시작하려면: net start Redis 
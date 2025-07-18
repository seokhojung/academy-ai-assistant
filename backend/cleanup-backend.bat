@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Backend Cleanup & Restart
echo ========================================

REM 포트 8000 사용 중인 프로세스 종료
echo Stopping backend server...
netstat -ano | findstr :8000 >nul
if not errorlevel 1 (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        echo Stopping process PID: %%a
        taskkill /f /pid %%a >nul 2>&1
    )
    timeout /t 3 >nul
    echo Backend server stopped.
) else (
    echo Backend server is not running.
)

REM 캐시 파일 정리
echo Cleaning cache files...
if exist __pycache__ (
    rmdir /s /q __pycache__
    echo Removed __pycache__
)
if exist app\__pycache__ (
    rmdir /s /q app\__pycache__
    echo Removed app\__pycache__
)
if exist app\api\__pycache__ (
    rmdir /s /q app\api\__pycache__
    echo Removed app\api\__pycache__
)
if exist app\api\v1\__pycache__ (
    rmdir /s /q app\api\v1\__pycache__
    echo Removed app\api\v1\__pycache__
)

REM 로그 파일 정리 (30일 이상 된 파일)
echo Cleaning old log files...
if exist logs (
    forfiles /p logs /s /m *.log /d -30 /c "cmd /c del @path" >nul 2>&1
    echo Cleaned logs older than 30 days
)

REM 데이터베이스 백업 (선택사항)
echo.
set /p backup="Do you want to backup the database? (y/n): "
if /i "%backup%"=="y" (
    echo Creating database backup...
    if exist academy.db (
        copy academy.db academy_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db
        echo Database backed up
    )
)

echo.
echo Cleanup completed!
echo.
set /p restart="Do you want to restart the backend server? (y/n): "
if /i "%restart%"=="y" (
    echo Starting backend server...
    call start-backend.bat
) else (
    echo To start the server manually, run: start-backend.bat
)

echo.
pause 
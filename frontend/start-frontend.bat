@echo off
REM frontend 폴더에서 실행해야 함
cd /d %~dp0

REM Node.js 버전 체크
node --version >nul 2>&1 || (
    echo [오류] Node.js가 설치되지 않았습니다.
    echo Node.js를 설치한 후 다시 실행해주세요.
    pause
    exit /b 1
)

REM npm 버전 체크
npm --version >nul 2>&1 || (
    echo [오류] npm이 설치되지 않았습니다.
    echo npm을 설치한 후 다시 실행해주세요.
    pause
    exit /b 1
)

REM 의존성 자동 설치
if not exist node_modules (
    echo [정보] 의존성 설치 중...
    npm install
    if errorlevel 1 (
        echo [오류] 의존성 설치에 실패했습니다.
        pause
        exit /b 1
    )
    echo [성공] 의존성 설치 완료
)

REM .env 파일 체크
if not exist .env (
    echo [경고] .env 파일이 없습니다.
    echo .env.example을 참고하여 .env 파일을 생성해주세요.
    echo 필수 환경변수:
    echo   - NEXT_PUBLIC_API_URL
    echo   - NEXT_PUBLIC_FIREBASE_*
    pause
)

REM 개발 서버 실행
echo [정보] 개발 서버 시작 중...
npm run dev 
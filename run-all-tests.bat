@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Academy AI Assistant 통합 테스트 실행
echo ============================================================
echo.

:: 환경 변수 설정
set BACKEND_DIR=backend
set FRONTEND_DIR=frontend

:: 색상 설정
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

:: 테스트 결과 저장
set TOTAL_TESTS=0
set PASSED_TESTS=0
set FAILED_TESTS=0

echo %BLUE%테스트 실행 전 확인사항:%RESET%
echo 1. FastAPI 서버가 실행 중인지 확인
echo 2. Next.js 개발 서버가 실행 중인지 확인  
echo 3. Celery 워커가 실행 중인지 확인
echo 4. Redis 서버가 실행 중인지 확인
echo 5. 환경 변수가 올바르게 설정되었는지 확인
echo.

set /p "continue=계속하시겠습니까? (y/n): "
if /i not "%continue%"=="y" (
    echo 테스트를 취소했습니다.
    goto :end
)

echo.
echo %BLUE%=== 1단계: 백엔드 API 테스트 ===%RESET%
echo.

:: 백엔드 디렉토리로 이동
cd /d "%BACKEND_DIR%"

:: 가상환경 활성화
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo %GREEN%가상환경 활성화 완료%RESET%
) else (
    echo %RED%가상환경을 찾을 수 없습니다. 먼저 가상환경을 생성해주세요.%RESET%
    goto :end
)

:: 실제 API 테스트 실행
echo.
echo %YELLOW%실행 중: 실제 API 테스트 (JWT 토큰 인증)...%RESET%
python test-api.py
if %errorlevel% equ 0 (
    echo %GREEN%✅ API 테스트 성공%RESET%
    set /a PASSED_TESTS+=1
) else (
    echo %RED%❌ API 테스트 실패%RESET%
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

:: Excel 재생성 테스트 실행
echo.
echo %YELLOW%실행 중: Excel 재생성 테스트 (실제 데이터)...%RESET%
python test-excel-rebuild.py
if %errorlevel% equ 0 (
    echo %GREEN%✅ Excel 재생성 테스트 성공%RESET%
    set /a PASSED_TESTS+=1
) else (
    echo %RED%❌ Excel 재생성 테스트 실패%RESET%
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

:: AI 채팅 테스트 실행
echo.
echo %YELLOW%실행 중: AI 채팅 테스트 (자연어 질문 및 응답)...%RESET%
python test-ai-chat.py
if %errorlevel% equ 0 (
    echo %GREEN%✅ AI 채팅 테스트 성공%RESET%
    set /a PASSED_TESTS+=1
) else (
    echo %RED%❌ AI 채팅 테스트 실패%RESET%
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

:: 통합 테스트 실행
echo.
echo %YELLOW%실행 중: 통합 테스트 (모든 기능)...%RESET%
python test-integration.py
if %errorlevel% equ 0 (
    echo %GREEN%✅ 통합 테스트 성공%RESET%
    set /a PASSED_TESTS+=1
) else (
    echo %RED%❌ 통합 테스트 실패%RESET%
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

:: 프로젝트 루트로 복귀
cd /d ".."

echo.
echo %BLUE%=== 2단계: 프론트엔드 연동 테스트 ===%RESET%
echo.

:: 프론트엔드 디렉토리로 이동
cd /d "%FRONTEND_DIR%"

:: Node.js 환경 확인
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%Node.js가 설치되지 않았습니다.%RESET%
    goto :end
)

:: 의존성 설치 확인
if not exist "node_modules" (
    echo %YELLOW%의존성을 설치합니다...%RESET%
    npm install
    if %errorlevel% neq 0 (
        echo %RED%의존성 설치에 실패했습니다.%RESET%
        goto :end
    )
)

:: 프론트엔드 연동 테스트 실행
echo.
echo %YELLOW%실행 중: 프론트엔드 연동 테스트 (Next.js와 백엔드 연동)...%RESET%
node test-integration.js
if %errorlevel% equ 0 (
    echo %GREEN%✅ 프론트엔드 연동 테스트 성공%RESET%
    set /a PASSED_TESTS+=1
) else (
    echo %RED%❌ 프론트엔드 연동 테스트 실패%RESET%
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

:: Jest 테스트 실행
echo.
echo %YELLOW%실행 중: Jest 단위 테스트...%RESET%
npm test -- --passWithNoTests
if %errorlevel% equ 0 (
    echo %GREEN%✅ Jest 테스트 성공%RESET%
    set /a PASSED_TESTS+=1
) else (
    echo %RED%❌ Jest 테스트 실패%RESET%
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

:: Playwright E2E 테스트 실행
echo.
echo %YELLOW%실행 중: Playwright E2E 테스트...%RESET%
npx playwright test --headed
if %errorlevel% equ 0 (
    echo %GREEN%✅ Playwright E2E 테스트 성공%RESET%
    set /a PASSED_TESTS+=1
) else (
    echo %RED%❌ Playwright E2E 테스트 실패%RESET%
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

:: 프로젝트 루트로 복귀
cd /d ".."

echo.
echo %BLUE%=== 3단계: 전체 시스템 테스트 ===%RESET%
echo.

:: Docker 컨테이너 테스트 (선택사항)
set /p "docker_test=Docker 컨테이너 테스트를 실행하시겠습니까? (y/n): "
if /i "%docker_test%"=="y" (
    echo.
    echo %YELLOW%실행 중: Docker 컨테이너 테스트...%RESET%
    docker-compose up -d
    timeout /t 30 /nobreak >nul
    
    :: 컨테이너 상태 확인
    docker-compose ps
    if %errorlevel% equ 0 (
        echo %GREEN%✅ Docker 컨테이너 테스트 성공%RESET%
        set /a PASSED_TESTS+=1
    ) else (
        echo %RED%❌ Docker 컨테이너 테스트 실패%RESET%
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
    
    :: 컨테이너 정리
    docker-compose down
)

:: 성능 테스트 (선택사항)
set /p "perf_test=성능 테스트를 실행하시겠습니까? (y/n): "
if /i "%perf_test%"=="y" (
    echo.
    echo %YELLOW%실행 중: 성능 테스트...%RESET%
    
    :: 백엔드 성능 테스트
    cd /d "%BACKEND_DIR%"
    python -c "
import time
import requests
start_time = time.time()
for i in range(10):
    requests.get('http://localhost:8000/health')
end_time = time.time()
avg_time = (end_time - start_time) / 10
print(f'평균 응답 시간: {avg_time:.3f}초')
"
    if %errorlevel% equ 0 (
        echo %GREEN%✅ 성능 테스트 성공%RESET%
        set /a PASSED_TESTS+=1
    ) else (
        echo %RED%❌ 성능 테스트 실패%RESET%
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
    
    cd /d ".."
)

:: 최종 결과 요약
echo.
echo %BLUE%============================================================%RESET%
echo %BLUE%                    테스트 결과 요약%RESET%
echo %BLUE%============================================================%RESET%
echo.
echo 총 테스트: %TOTAL_TESTS%
echo 성공: %GREEN%%PASSED_TESTS%%RESET%
echo 실패: %RED%%FAILED_TESTS%%RESET%

if %TOTAL_TESTS% gtr 0 (
    set /a "success_rate=(PASSED_TESTS * 100) / TOTAL_TESTS"
    echo 성공률: %success_rate%%%
)

echo.

if %FAILED_TESTS% equ 0 (
    echo %GREEN%🎉 모든 테스트가 성공했습니다!%RESET%
    echo.
    echo %BLUE%다음 단계:%RESET%
    echo 1. 실제 사용자와의 테스트
    echo 2. 성능 최적화
    echo 3. 보안 강화
    echo 4. 프로덕션 배포
) else (
    echo %RED%⚠️  일부 테스트가 실패했습니다.%RESET%
    echo.
    echo %BLUE%확인이 필요한 항목:%RESET%
    echo 1. 서버 실행 상태
    echo 2. 환경 변수 설정
    echo 3. 의존성 설치 상태
    echo 4. 네트워크 연결 상태
    echo 5. API 엔드포인트 구현 상태
)

echo.
echo %BLUE%테스트 로그 파일:%RESET%
echo - 백엔드: %BACKEND_DIR%\test-results.log
echo - 프론트엔드: %FRONTEND_DIR%\test-results.log
echo.

:end
echo.
echo %BLUE%테스트 실행이 완료되었습니다.%RESET%
echo 아무 키나 누르면 종료됩니다...
pause >nul 
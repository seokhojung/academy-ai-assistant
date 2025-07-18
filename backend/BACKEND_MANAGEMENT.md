# 백엔드 관리 가이드

## 개요
Academy AI Assistant 백엔드 서버의 효율적인 관리와 운영을 위한 가이드입니다.

## 스크립트 파일들

### 1. `start-backend.bat` - 서버 시작
```bash
# 백엔드 서버를 시작합니다
start-backend.bat
```

**기능:**
- 가상환경 자동 생성 및 활성화
- 의존성 자동 설치 확인
- 포트 충돌 자동 해결
- 서버 상태 정보 표시

### 2. `check-backend.bat` - 상태 확인
```bash
# 백엔드 상태를 확인합니다
check-backend.bat
```

**확인 항목:**
- 서버 실행 상태 (포트 8000)
- API 엔드포인트 응답
- 데이터베이스 연결 상태
- 의존성 설치 상태

### 3. `cleanup-backend.bat` - 정리 및 재시작
```bash
# 백엔드를 정리하고 재시작합니다
cleanup-backend.bat
```

**정리 항목:**
- 실행 중인 서버 종료
- Python 캐시 파일 정리
- 오래된 로그 파일 정리
- 데이터베이스 백업 (선택사항)

## API 엔드포인트

### 헬스체크
```bash
GET http://localhost:8000/health
```

**응답 예시:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-19T10:00:00Z",
  "version": "1.0.0",
  "database": "healthy",
  "environment": "development"
}
```

### API 문서
```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc
```

## 로그 관리

### 로그 위치
```
backend/logs/
├── backend_2024-12-19.log
├── backend_2024-12-18.log
└── ...
```

### 로그 설정
- **파일 크기**: 최대 10MB
- **보관 기간**: 30일
- **로그 레벨**: INFO
- **SQL 쿼리**: WARNING 이상만

## 데이터베이스 관리

### SQLite 데이터베이스
- **파일**: `academy.db`
- **백업**: `cleanup-backend.bat`에서 자동 백업 가능
- **위치**: `backend/` 디렉토리

### PostgreSQL (선택사항)
- 환경변수 `DATABASE_URL` 설정 필요
- `psycopg2-binary` 패키지 사용

## 의존성 관리

### 주요 패키지
```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlalchemy==2.0.23
sqlmodel==0.0.16

# Authentication
firebase-admin==6.2.0
python-jose[cryptography]==3.3.0

# AI Integration
google-generativeai==0.3.2
```

### 의존성 업데이트
```bash
# 가상환경 활성화
venv\Scripts\activate.bat

# 패키지 업데이트
pip install -r requirements.txt --upgrade

# 새로운 패키지 추가 시
pip install package_name
pip freeze > requirements.txt
```

## 문제 해결

### 1. 포트 충돌
```bash
# 포트 사용 확인
netstat -ano | findstr :8000

# 프로세스 종료
taskkill /f /pid [PID]
```

### 2. 의존성 오류
```bash
# 가상환경 재생성
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 3. 데이터베이스 오류
```bash
# 데이터베이스 파일 확인
dir academy.db

# 백업에서 복원
copy academy_backup_YYYYMMDD.db academy.db
```

### 4. 로그 확인
```bash
# 최신 로그 확인
type logs\backend_%date:~-4,4%-%date:~-10,2%-%date:~-7,2%.log

# 에러 로그 필터링
findstr "ERROR" logs\backend_*.log
```

## 성능 최적화

### 1. 메모리 사용량
- 로그 파일 크기 제한 (10MB)
- 30일 이상 된 로그 자동 삭제
- SQL 쿼리 로그 레벨 조정

### 2. 응답 시간
- 데이터베이스 인덱스 최적화
- 캐시 파일 정기 정리
- 불필요한 로그 레벨 조정

### 3. 안정성
- 헬스체크 엔드포인트 모니터링
- 자동 재시작 기능
- 데이터베이스 백업 자동화

## 배포 고려사항

### 1. 환경변수
```bash
# 개발 환경
ENVIRONMENT=development
DATABASE_URL=sqlite:///./academy.db

# 프로덕션 환경
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@host:port/db
```

### 2. 보안
- CORS 설정 확인
- 환경변수 보안 관리
- API 키 보안 처리

### 3. 모니터링
- 헬스체크 엔드포인트 활용
- 로그 파일 모니터링
- 성능 메트릭 수집

## 개발 워크플로우

### 1. 개발 시작
```bash
# 1. 상태 확인
check-backend.bat

# 2. 필요시 정리
cleanup-backend.bat

# 3. 서버 시작
start-backend.bat
```

### 2. 코드 변경 후
```bash
# 자동 리로드 (uvicorn --reload)
# 또는 수동 재시작
cleanup-backend.bat
```

### 3. 배포 전
```bash
# 1. 테스트 실행
pytest

# 2. 로그 확인
check-backend.bat

# 3. 데이터베이스 백업
cleanup-backend.bat (백업 선택)
``` 
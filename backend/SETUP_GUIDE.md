# Academy AI Assistant 설정 및 실행 가이드

## 🚀 빠른 시작

### 1단계: Redis 설치 및 실행

```bash
# Redis 설치 스크립트 실행 (관리자 권한 필요)
install-redis.bat

# 또는 수동 설치:
# 1. https://github.com/microsoftarchive/redis/releases 에서 Redis-x64-5.0.14.1.msi 다운로드
# 2. 설치 후 서비스 시작: net start Redis
```

### 2단계: Gemini API 키 발급

1. [Google AI Studio](https://aistudio.google.com/) 접속
2. "Get API key" → "Create API key" 클릭
3. API 키 복사 후 `backend/.env` 파일에 설정:

```env
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

### 3단계: Google Cloud Storage 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. `GCS_SETUP.md` 파일의 단계별 가이드 따라하기
3. 서비스 계정 키 파일을 `backend/gcs-service-account.json`으로 저장
4. `backend/.env` 파일에 설정:

```env
GCS_BUCKET_NAME=academy-ai-assistant-files
GCS_CREDENTIALS_PATH=./gcs-service-account.json
```

### 4단계: 환경 변수 설정

`backend/.env` 파일 생성:

```env
# AI
GEMINI_API_KEY=your-gemini-api-key

# Redis (Celery 브로커)
REDIS_URL=redis://localhost:6379

# Google Cloud Storage
GCS_BUCKET_NAME=academy-ai-assistant-files
GCS_CREDENTIALS_PATH=./gcs-service-account.json

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# Database
DATABASE_URL=sqlite:///./academy_ai.db

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Environment
ENVIRONMENT=development
DEBUG=true
```

### 5단계: 패키지 설치

```bash
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 6단계: 통합 테스트

```bash
# 모든 기능 테스트
python test-integration.py
```

### 7단계: 서버 실행

```bash
# 터미널 1: FastAPI 서버
start-backend.bat

# 터미널 2: Celery 워커
start-celery.bat

# 터미널 3: 프론트엔드 (선택사항)
cd ../frontend
start-frontend.bat
```

## 📋 상세 설정 가이드

### Redis 설정
- **설치**: `install-redis.bat` 실행 또는 수동 설치
- **확인**: `redis-cli ping` → `PONG` 응답 확인
- **서비스**: `net start Redis` / `net stop Redis`

### Gemini API 설정
- **발급**: [Google AI Studio](https://aistudio.google.com/)
- **제한**: 분당 60회 요청 (무료)
- **테스트**: `GEMINI_SETUP.md` 참조

### Google Cloud Storage 설정
- **버킷**: `academy-ai-assistant-files` 생성
- **권한**: Storage Object Admin 역할 부여
- **키**: 서비스 계정 JSON 키 파일 다운로드
- **테스트**: `GCS_SETUP.md` 참조

## 🧪 테스트 방법

### 1. 통합 테스트
```bash
python test-integration.py
```

### 2. 개별 기능 테스트

#### Redis 테스트
```python
import redis
r = redis.from_url('redis://localhost:6379')
r.ping()  # PONG 응답 확인
```

#### Gemini API 테스트
```python
import google.generativeai as genai
genai.configure(api_key='your-api-key')
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("테스트")
print(response.text)
```

#### GCS 테스트
```python
from google.cloud import storage
client = storage.Client()
bucket = client.bucket('academy-ai-assistant-files')
print(bucket.exists())  # True 확인
```

#### FastAPI 테스트
```bash
curl http://localhost:8000/health
```

### 3. API 엔드포인트 테스트

#### AI 채팅 테스트
```bash
curl -X POST "http://localhost:8000/api/v1/ai/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "안녕하세요!"}'
```

#### Excel 재생성 테스트
```bash
curl -X POST "http://localhost:8000/api/v1/excel/rebuild/students" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔧 문제 해결

### Redis 연결 오류
```bash
# Redis 서비스 상태 확인
sc query Redis

# Redis 서비스 재시작
net stop Redis
net start Redis

# 포트 확인
netstat -an | findstr 6379
```

### Gemini API 오류
```bash
# API 키 확인
echo %GEMINI_API_KEY%

# Python에서 테스트
python -c "import google.generativeai as genai; genai.configure(api_key='your-key'); print('OK')"
```

### GCS 연결 오류
```bash
# 서비스 계정 키 파일 확인
dir gcs-service-account.json

# 환경 변수 확인
echo %GCS_CREDENTIALS_PATH%
echo %GCS_BUCKET_NAME%
```

### Celery 워커 오류
```bash
# Redis 연결 확인
redis-cli ping

# Celery 상태 확인
celery -A app.workers.celery_app inspect active
```

## 📊 모니터링

### 로그 확인
```bash
# FastAPI 로그
tail -f logs/fastapi.log

# Celery 로그
tail -f logs/celery.log
```

### 상태 확인
```bash
# Redis 상태
redis-cli info

# Celery 상태
celery -A app.workers.celery_app inspect stats

# API 상태
curl http://localhost:8000/health
```

## 🚀 배포 준비

### 프로덕션 환경 변수
```env
ENVIRONMENT=production
DEBUG=false
JWT_SECRET_KEY=very-secure-production-key
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://production-redis:6379
```

### Docker 배포
```bash
docker build -t academy-ai-backend .
docker run -p 8000:8000 academy-ai-backend
```

## 📞 지원

문제가 발생하면:
1. `test-integration.py` 실행하여 진단
2. 로그 파일 확인
3. 환경 변수 설정 재확인
4. 각 서비스 개별 테스트

## 🎯 다음 단계

설정 완료 후:
1. 프론트엔드 연동 테스트
2. 실제 데이터로 Excel 재생성 테스트
3. AI 채팅 기능 활용
4. 성능 모니터링 및 최적화 
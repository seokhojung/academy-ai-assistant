# Academy AI Assistant Backend

FastAPI 기반의 AI 학원 관리 시스템 백엔드입니다.

## 주요 기능

- **학생/강사/교재 CRUD API**
- **JWT + Firebase 인증**
- **AI 채팅 (Gemini API)**
- **Excel 자동 재생성 (Celery + portalocker)**
- **Google Cloud Storage 연동**

## 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate.bat

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 설정하세요:

```env
# AI
GEMINI_API_KEY=your-gemini-api-key

# Redis (Celery 브로커)
REDIS_URL=redis://localhost:6379

# Google Cloud Storage
GCS_BUCKET_NAME=academy-ai-assistant-files
GCS_CREDENTIALS_PATH=path/to/service-account-key.json

# 기타 설정은 env.example 참조
```

### 3. 서버 실행

```bash
# FastAPI 서버 실행
start-backend.bat

# Celery 워커 실행 (별도 터미널)
start-celery.bat
```

## API 엔드포인트

### 인증
- `POST /api/v1/auth/login` - JWT 로그인
- `POST /api/v1/auth/firebase` - Firebase 토큰 검증
- `GET /api/v1/auth/me` - 내 정보

### 학생 관리
- `GET /api/v1/students/` - 학생 목록
- `POST /api/v1/students/` - 학생 등록
- `GET /api/v1/students/{id}` - 학생 상세
- `PUT /api/v1/students/{id}` - 학생 수정
- `DELETE /api/v1/students/{id}` - 학생 삭제

### 강사 관리
- `GET /api/v1/teachers/` - 강사 목록
- `POST /api/v1/teachers/` - 강사 등록
- `GET /api/v1/teachers/{id}` - 강사 상세
- `PUT /api/v1/teachers/{id}` - 강사 수정
- `DELETE /api/v1/teachers/{id}` - 강사 삭제

### 교재 관리
- `GET /api/v1/materials/` - 교재 목록
- `POST /api/v1/materials/` - 교재 등록
- `GET /api/v1/materials/{id}` - 교재 상세
- `PUT /api/v1/materials/{id}` - 교재 수정
- `DELETE /api/v1/materials/{id}` - 교재 삭제

### AI 채팅
- `POST /api/v1/ai/chat` - AI 채팅
- `POST /api/v1/ai/chat/stream` - AI 스트리밍 채팅
- `POST /api/v1/ai/analyze` - 학습 분석
- `POST /api/v1/ai/command` - 자연어 명령 처리

### Excel 재생성
- `POST /api/v1/excel/rebuild/students` - 학생 Excel 재생성
- `POST /api/v1/excel/rebuild/teachers` - 강사 Excel 재생성
- `POST /api/v1/excel/rebuild/materials` - 교재 Excel 재생성
- `POST /api/v1/excel/rebuild/all` - 전체 Excel 재생성
- `GET /api/v1/excel/status/{task_id}` - 재생성 상태 확인

## Excel Rebuilder 기능

### 특징
- **자동 재생성**: 데이터 변경 시 Excel 파일 자동 업데이트
- **파일 잠금**: portalocker를 통한 동시 편집 방지
- **비동기 처리**: Celery를 통한 백그라운드 처리
- **GCS 업로드**: Google Cloud Storage에 자동 업로드
- **진행 상황 추적**: 실시간 처리 상태 확인

### 사용법

1. **Excel 재생성 요청**
```bash
curl -X POST "http://localhost:8000/api/v1/excel/rebuild/students" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

2. **상태 확인**
```bash
curl -X GET "http://localhost:8000/api/v1/excel/status/TASK_ID" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## AI 채팅 기능

### 특징
- **Gemini 1.5 Flash API**: Google의 최신 AI 모델 사용
- **자연어 처리**: 학원 관리 관련 질문에 특화된 응답
- **스트리밍 응답**: 실시간 AI 응답 스트리밍
- **학습 분석**: 학생 데이터 기반 개인화된 분석
- **명령 처리**: 자연어를 구조화된 명령으로 변환

### 사용법

1. **일반 채팅**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "김철수 학생의 수강료 납부 현황을 알려주세요"}'
```

2. **스트리밍 채팅**
```bash
curl -X POST "http://localhost:8000/api/v1/ai/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "오늘 출석한 학생들을 보여주세요"}'
```

## 개발 환경

### 필수 요구사항
- Python 3.11+
- Redis (Celery 브로커)
- Google Cloud Storage (선택사항)

### 개발 도구
- FastAPI
- SQLModel
- Celery
- Google Generative AI
- Firebase Admin SDK

## 배포

### Docker 사용
```bash
docker build -t academy-ai-backend .
docker run -p 8000:8000 academy-ai-backend
```

### 환경 변수
프로덕션 환경에서는 다음 환경 변수를 설정하세요:
- `GEMINI_API_KEY`: 실제 Gemini API 키
- `REDIS_URL`: 프로덕션 Redis URL
- `GCS_CREDENTIALS_PATH`: GCS 서비스 계정 키 경로
- `JWT_SECRET_KEY`: 강력한 JWT 시크릿 키

## 문제 해결

### 일반적인 문제
1. **Redis 연결 오류**: Redis 서버가 실행 중인지 확인
2. **Gemini API 오류**: API 키가 올바른지 확인
3. **GCS 업로드 오류**: 서비스 계정 키 경로 확인
4. **Celery 워커 오류**: 가상환경 활성화 및 PYTHONPATH 확인

### 로그 확인
```bash
# FastAPI 로그
tail -f logs/fastapi.log

# Celery 로그
tail -f logs/celery.log
``` 
# Render 배포 가이드

## 필수 환경 변수 설정

Render 대시보드에서 다음 환경 변수들을 설정해야 합니다:

### 기본 설정
```
ENVIRONMENT=production
DEBUG=false
```

### 데이터베이스 (PostgreSQL)
```
DATABASE_URL=postgresql://username:password@host:port/database_name
```
- Render PostgreSQL 서비스에서 제공하는 연결 문자열 사용

### Redis (선택사항)
```
REDIS_URL=redis://username:password@host:port
```
- Redis가 필요한 경우에만 설정

### JWT 인증
```
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Firebase (선택사항)
```
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_PROJECT_ID=your-firebase-project-id
```

### Gemini API (선택사항)
```
GEMINI_API_KEY=your-gemini-api-key
```

### Google Cloud Storage (선택사항)
```
GCS_BUCKET_NAME=your-bucket-name
GCS_CREDENTIALS_PATH=path/to/service-account-key.json
```

## 배포 설정

### 빌드 명령어
```
pip install -r requirements.txt
```

### 시작 명령어
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Python 버전
```
3.11
```

## 주의사항

1. **데이터베이스**: SQLite는 배포 환경에서 권장되지 않습니다. PostgreSQL을 사용하세요.
2. **환경 변수**: 민감한 정보는 반드시 환경 변수로 설정하세요.
3. **CORS**: 프로덕션 환경에서는 실제 도메인을 CORS 설정에 추가하세요.
4. **포트**: Render는 `$PORT` 환경 변수를 자동으로 제공합니다.

## 문제 해결

### pydantic_settings 오류
- `requirements.txt`에 `pydantic-settings==2.0.3`이 포함되어 있는지 확인

### 데이터베이스 연결 오류
- `DATABASE_URL`이 올바르게 설정되어 있는지 확인
- PostgreSQL 서비스가 활성화되어 있는지 확인

### 포트 오류
- 시작 명령어에서 `$PORT` 환경 변수를 사용하고 있는지 확인 
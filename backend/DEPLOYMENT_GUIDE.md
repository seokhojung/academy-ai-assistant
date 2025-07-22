# 🚀 배포 환경 설정 가이드

## 📋 개요

이 가이드는 Academy AI Assistant를 다양한 환경에 배포할 때 API 키와 환경변수를 안전하게 설정하는 방법을 설명합니다.

## 🔐 보안 원칙

1. **API 키는 절대 Git에 커밋하지 않음**
2. **환경별로 다른 설정 사용**
3. **프로덕션에서는 강력한 시크릿 키 사용**
4. **정기적인 키 교체**

## 🏗️ 환경별 설정

### 개발환경 (Development)

```bash
# .env 파일 생성
cp env.example .env

# 개발환경 설정
ENVIRONMENT=development
DEBUG=true
GEMINI_API_KEY=your-actual-api-key  # 실제 API 키 또는 빈 값
DATABASE_URL=sqlite:///./academy.db
```

**특징:**
- SQLite 데이터베이스 사용
- 디버그 모드 활성화

### 프로덕션환경 (Production)

```bash
# 환경변수 설정 (서버에서)
export ENVIRONMENT=production
export DEBUG=false
export GEMINI_API_KEY=your-production-api-key  # 반드시 유효한 API 키
export DATABASE_URL=postgresql://user:password@host:5432/dbname
export JWT_SECRET_KEY=super-strong-random-secret-key
```

**특징:**
- API 키가 반드시 필요
- PostgreSQL 데이터베이스 사용
- 디버그 모드 비활성화

## 🌐 배포 플랫폼별 설정

### Vercel 배포

1. **Vercel 대시보드에서 환경변수 설정:**
   ```
   ENVIRONMENT=production
   GEMINI_API_KEY=your-gemini-api-key
   JWT_SECRET_KEY=your-jwt-secret
   DATABASE_URL=your-postgresql-url
   ```

2. **환경변수 우선순위:**
   - Production: 프로덕션 환경변수
   - Preview: 개발 환경변수

### Docker 배포

```dockerfile
# Dockerfile 예시
FROM python:3.11-slim

# 환경변수 설정
ENV ENVIRONMENT=production
ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV JWT_SECRET_KEY=${JWT_SECRET_KEY}

# 애플리케이션 실행
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Docker 실행 시 환경변수 전달
docker run -e GEMINI_API_KEY=your-key -e JWT_SECRET_KEY=your-secret your-app
```

### Kubernetes 배포

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: academy-ai-assistant
spec:
  template:
    spec:
      containers:
      - name: app
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: gemini-api-key
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: jwt-secret
```

## 🔧 API 키 관리

### Gemini API 키 설정

1. **Google AI Studio에서 API 키 생성:**
   - https://makersuite.google.com/app/apikey
   - 새 API 키 생성
   - 키 제한 설정 (선택사항)

2. **환경변수에 설정:**
   ```bash
   # 개발환경
   export GEMINI_API_KEY=AIzaSyC...
   
   # 프로덕션환경
   export GEMINI_API_KEY=AIzaSyC...
   ```

3. **키 보안:**
   - 정기적으로 키 교체 (3-6개월)
   - 사용량 모니터링
   - 키 제한 설정 (도메인, IP 등)

### JWT 시크릿 키 생성

```python
# 강력한 JWT 시크릿 키 생성
import secrets
print(secrets.token_urlsafe(32))
```

## 🧪 테스트 및 검증

### AI 서비스 상태 확인

```bash
# API 상태 확인
curl http://localhost:8000/api/v1/ai/status

# 응답 예시
{
  "status": "active",
  "api_key_configured": true,
  "api_key_preview": "AIza...SyC",
  "environment": "production",
  "debug": false
}
```

### 환경별 동작 확인

1. **개발환경:**
   - API 키 설정 필요
   - 테스트용 응답 제공

2. **프로덕션환경:**
   - API 키가 반드시 필요
   - 실제 Gemini API 사용

## 🚨 문제 해결

### 일반적인 문제

1. **API 키 인증 오류:**
   ```bash
   # 키 유효성 확인
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        https://generativelanguage.googleapis.com/v1beta/models
   ```

2. **환경변수 로드 실패:**
   ```bash
   # 환경변수 확인
   echo $GEMINI_API_KEY
   echo $ENVIRONMENT
   ```

3. **API 키 미설정:**
   ```bash
   # API 키 설정 확인
   echo $GEMINI_API_KEY
   ```

### 로그 확인

```bash
# 애플리케이션 로그 확인
tail -f logs/app.log

# AI 서비스 로그
grep "\[AI\]" logs/app.log
```

## 📚 추가 리소스

- [Google AI Studio](https://makersuite.google.com/)
- [FastAPI 환경변수](https://fastapi.tiangolo.com/advanced/settings/)
- [Python-decouple](https://github.com/henriquebastos/python-decouple)
- [Vercel 환경변수](https://vercel.com/docs/concepts/projects/environment-variables)

## 🔄 업데이트 및 유지보수

1. **정기적인 API 키 교체**
2. **환경변수 백업**
3. **보안 감사**
4. **성능 모니터링**

---

**⚠️ 주의사항:** 이 가이드의 설정을 따라하기 전에 보안 정책을 검토하고, 조직의 보안 요구사항에 맞게 조정하세요. 
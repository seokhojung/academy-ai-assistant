# AI 챗봇 설정 및 배포 가이드

## 🚀 빠른 시작

### 1. 로컬 개발 환경 설정

```bash
# 1. 환경변수 파일 생성
cp env.example .env

# 2. .env 파일 편집하여 Gemini API 키 설정
GEMINI_API_KEY=your-actual-gemini-api-key-here

# 3. 백엔드 서버 시작
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. AI 챗봇 테스트

```bash
# AI 챗봇 테스트 스크립트 실행
python test-ai-chat.py
```

## 🔧 환경별 설정

### 개발 환경 (Development)

```env
ENVIRONMENT=development
DEBUG=true
GEMINI_API_KEY=your-gemini-api-key-here
```

**특징:**
- Mock AI 모드 지원 (API 키 없이도 테스트 가능)
- 상세한 디버그 로그
- 로컬 테스트 도구 제공

### 프로덕션 환경 (Production)

```env
ENVIRONMENT=production
DEBUG=false
GEMINI_API_KEY=your-production-gemini-api-key
```

**특징:**
- 실제 Gemini API 사용
- 보안 강화
- 성능 최적화

## 🤖 AI 모드 설명

### Mock AI 모드 (개발 환경에서만)
- **용도**: 개발 및 테스트
- **특징**: 
  - Gemini API 키 없이도 작동
  - 미리 정의된 응답 제공
  - 빠른 응답 속도
- **활성화 조건**: 개발 환경에서 `GEMINI_API_KEY`가 설정되지 않음

### Real AI 모드 (API 키 있음)
- **용도**: 실제 서비스
- **특징**:
  - 실제 Gemini API 사용
  - 동적 응답 생성
  - 고품질 AI 응답
- **활성화 조건**: 유효한 `GEMINI_API_KEY` 설정

## 📊 API 엔드포인트

### 테스트용 (인증 없음)
```http
GET  /api/v1/ai/status          # AI 서비스 상태 확인
POST /api/v1/ai/chat/test       # AI 챗봇 테스트
```

### 실제 서비스용 (인증 필요)
```http
POST /api/v1/ai/chat            # AI 챗봇
POST /api/v1/ai/chat/stream     # AI 챗봇 스트리밍
POST /api/v1/ai/analyze         # 학습 분석
POST /api/v1/ai/command         # 자연어 명령 처리
```

## 🧪 테스트 방법

### 1. 자동 테스트
```bash
python test-ai-chat.py
```

### 2. 수동 테스트
```bash
# 서버 상태 확인
curl http://localhost:8000/api/v1/ai/status

# AI 챗봇 테스트
curl -X POST http://localhost:8000/api/v1/ai/chat/test \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕하세요"}'
```

### 3. 프론트엔드 테스트
- 브라우저에서 `http://localhost:3000/ai-chat` 접속
- AI 챗봇 인터페이스에서 직접 테스트

## 🔍 디버깅

### 로그 확인
```bash
# 백엔드 서버 로그에서 AI 관련 메시지 확인
[AI] Gemini API 설정 완료: AIza...abcd
[AI] Mock AI 모드 활성화 (개발 환경)
[AI] Gemini API 호출 오류: ...
```

### 상태 확인
```bash
# AI 서비스 상태 확인
curl http://localhost:8000/api/v1/ai/status
```

응답 예시:
```json
{
  "status": "active",
  "api_key_configured": true,
  "api_key_preview": "AIza...abcd",
  "environment": "development",
  "debug": true
}
```

## 🚀 배포 가이드

### Vercel 배포
1. **환경변수 설정**:
   - Vercel 대시보드 → Project Settings → Environment Variables
   - `GEMINI_API_KEY` 추가

2. **배포 확인**:
   ```bash
   # 배포 후 AI 상태 확인
   curl https://your-app.vercel.app/api/v1/ai/status
   ```

### Docker 배포
```dockerfile
# Dockerfile에 환경변수 추가
ENV GEMINI_API_KEY=your-gemini-api-key
```

### 기타 클라우드 서비스
- **AWS**: ECS, Lambda 환경변수 설정
- **GCP**: Cloud Run 환경변수 설정
- **Azure**: App Service 애플리케이션 설정

## 🔒 보안 고려사항

### API 키 보안
- ✅ 환경변수로 관리
- ✅ 프로덕션에서만 실제 키 사용
- ✅ 키 순환 정책 수립
- ❌ 코드에 하드코딩 금지
- ❌ Git에 API 키 커밋 금지

### 접근 제어
- ✅ 인증된 사용자만 접근
- ✅ Rate Limiting 적용
- ✅ 입력 검증 및 필터링

## 📈 성능 최적화

### Mock 모드 최적화 (개발 환경)
- 빠른 응답을 위한 캐싱
- 미리 정의된 응답 사용

### Real AI 모드 최적화
- API 호출 최적화
- 응답 캐싱
- 스트리밍 응답 사용

## 🐛 문제 해결

### 일반적인 문제

1. **API 키 오류**
   ```
   [AI] Gemini API 설정 실패: Invalid API key
   ```
   **해결**: 유효한 Gemini API 키 확인

2. **서버 연결 실패**
   ```
   Connection error: Connection refused
   ```
   **해결**: 백엔드 서버 실행 확인

3. **Mock 모드 활성화 (개발 환경)**
   ```
   [AI] Mock AI 모드 활성화 (개발 환경)
   ```
   **해결**: 개발 환경에서는 정상, 프로덕션에서는 `GEMINI_API_KEY` 환경변수 설정

### 로그 분석
```bash
# 백엔드 로그에서 AI 관련 오류 확인
grep "\[AI\]" backend.log
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 환경변수 설정
2. 서버 로그
3. API 상태 엔드포인트
4. 테스트 스크립트 실행 결과 
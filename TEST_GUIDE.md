# Academy AI Assistant 테스트 가이드

## 📋 목차

1. [테스트 개요](#테스트-개요)
2. [사전 준비사항](#사전-준비사항)
3. [개별 테스트 실행](#개별-테스트-실행)
4. [통합 테스트 실행](#통합-테스트-실행)
5. [테스트 결과 해석](#테스트-결과-해석)
6. [문제 해결](#문제-해결)
7. [다음 단계](#다음-단계)

## 🎯 테스트 개요

Academy AI Assistant는 다음 4가지 주요 테스트를 제공합니다:

### 1. 실제 API 테스트 (JWT 토큰 인증)
- **목적**: 백엔드 API의 모든 엔드포인트가 정상 동작하는지 확인
- **범위**: 학생, 강사, 교재 CRUD, AI 채팅, Excel 재생성 API
- **파일**: `backend/test-api.py`

### 2. Excel 재생성 테스트 (실제 데이터)
- **목적**: Celery 워커와 Excel Rebuilder가 실제 데이터로 Excel 파일을 생성하는지 확인
- **범위**: 학생, 강사, 교재 Excel 파일 생성 및 다운로드
- **파일**: `backend/test-excel-rebuild.py`

### 3. AI 채팅 테스트 (자연어 질문 및 응답)
- **목적**: Gemini API 연동과 자연어 처리 기능이 정상 동작하는지 확인
- **범위**: 기본 채팅, 자연어 명령, 학습 분석, 대화 컨텍스트
- **파일**: `backend/test-ai-chat.py`

### 4. 프론트엔드 연동 테스트 (Next.js와 백엔드 연동)
- **목적**: Next.js 프론트엔드와 백엔드 API가 정상적으로 연동되는지 확인
- **범위**: API 연동, 인증, 페이지 접근, E2E 테스트
- **파일**: `frontend/test-integration.js`

## 🔧 사전 준비사항

### 필수 서비스 실행 확인

1. **FastAPI 서버**
   ```bash
   cd backend
   start-server.bat
   ```

2. **Next.js 개발 서버**
   ```bash
   cd frontend
   start-dev.bat
   ```

3. **Celery 워커** (Excel 재생성 테스트용)
   ```bash
   cd backend
   start-celery-worker.bat
   ```

4. **Redis 서버** (Celery 백엔드용)
   ```bash
   cd backend
   install-redis.bat
   ```

### 환경 변수 설정 확인

#### 백엔드 환경 변수 (`backend/.env`)
```env
# 데이터베이스
DATABASE_URL=postgresql://username:password@localhost:5432/academy_db

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Google Cloud Storage
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_BUCKET=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Redis
REDIS_URL=redis://localhost:6379/0
```

#### 프론트엔드 환경 변수 (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
```

## 🚀 개별 테스트 실행

### 1. 실제 API 테스트

```bash
cd backend
python test-api.py
```

**예상 결과:**
```
============================================================
  서버 상태 확인
============================================================
✅ PASS 서버 상태
   └─ 서버 정상 동작

============================================================
  Firebase 인증 테스트
============================================================
✅ PASS JWT 토큰 생성
   └─ 테스트용 토큰 생성 완료

============================================================
  학생 CRUD API 테스트
============================================================
✅ PASS 학생 목록 조회
   └─ 총 3명의 학생
✅ PASS 학생 등록
   └─ 학생 ID: 4
...
```

### 2. Excel 재생성 테스트

```bash
cd backend
python test-excel-rebuild.py
```

**예상 결과:**
```
============================================================
  테스트 데이터 생성
============================================================
✅ PASS 학생 생성: 김철수
✅ PASS 학생 생성: 이영희
✅ PASS 학생 생성: 박민수
✅ PASS 강사 생성: 김수학
✅ PASS 강사 생성: 이영어
✅ PASS 교재 생성: 수학의 정석
✅ PASS 교재 생성: 영어 문법 완성
✅ PASS 테스트 데이터 생성
   └─ 학생 3명, 강사 2명, 교재 2개

============================================================
  학생 Excel 재생성 테스트
============================================================
✅ PASS 학생 Excel 재생성 요청
   └─ 태스크 ID: abc123-def456
   └─ 상태 확인 (2초): PENDING
   └─ 상태 확인 (4초): SUCCESS
✅ PASS 학생 Excel 재생성 완료
   └─ 파일 경로: /app/excel/students_20241201_143022.xlsx
✅ PASS Excel 파일 다운로드
   └─ 파일 크기: 15420 bytes
```

### 3. AI 채팅 테스트

```bash
cd backend
python test-ai-chat.py
```

**예상 결과:**
```
============================================================
  기본 AI 채팅 테스트
============================================================
✅ PASS 기본 채팅 테스트 1
   └─ 응답 길이: 156 문자, 키워드: 학원, 관리, 시스템
   └─ 응답: 안녕하세요! 학원 관리 시스템은 학생, 강사, 교재를 효율적으로 관리할 수 있는 종합적인 플랫폼입니다...

============================================================
  자연어 명령 처리 테스트
============================================================
✅ PASS 자연어 명령 테스트 1
   └─ 액션: check_tuition_status, 엔티티: ['김철수', '학생', '수강료', '납부']
   └─ 파싱 결과: {'action': 'check_tuition_status', 'student_name': '김철수'}
```

### 4. 프론트엔드 연동 테스트

```bash
cd frontend
node test-integration.js
```

**예상 결과:**
```
============================================================
  백엔드 연결 테스트
============================================================
✅ PASS 백엔드 서버 연결
   └─ 서버 정상 동작

============================================================
  프론트엔드 연결 테스트
============================================================
✅ PASS 프론트엔드 서버 연결
   └─ 서버 정상 동작

============================================================
  학생 API 연동 테스트
============================================================
✅ PASS 학생 목록 조회
   └─ 총 3명의 학생
✅ PASS 학생 등록
   └─ 학생 ID: 5
✅ PASS 학생 상세 조회
   └─ 이름: 테스트 학생
```

## 🔄 통합 테스트 실행

모든 테스트를 한 번에 실행하려면:

```bash
run-all-tests.bat
```

**실행 과정:**
1. 사전 준비사항 확인
2. 백엔드 API 테스트 (4개)
3. 프론트엔드 연동 테스트 (3개)
4. Docker 컨테이너 테스트 (선택사항)
5. 성능 테스트 (선택사항)
6. 최종 결과 요약

**예상 결과:**
```
============================================================
                    테스트 결과 요약
============================================================

총 테스트: 7
성공: 7
실패: 0
성공률: 100%

🎉 모든 테스트가 성공했습니다!

다음 단계:
1. 실제 사용자와의 테스트
2. 성능 최적화
3. 보안 강화
4. 프로덕션 배포
```

## 📊 테스트 결과 해석

### 성공 지표

- **API 테스트**: 모든 CRUD 작업이 정상 동작
- **Excel 테스트**: 파일 생성 및 다운로드 성공
- **AI 테스트**: 자연어 응답 품질 확인
- **연동 테스트**: 프론트엔드-백엔드 통신 정상

### 실패 원인 분석

#### 1. 서버 연결 실패
```
❌ FAIL 서버 연결
   └─ 연결 실패: Connection refused
```
**해결방법:**
- 서버가 실행 중인지 확인
- 포트 번호 확인 (백엔드: 8000, 프론트엔드: 3000)
- 방화벽 설정 확인

#### 2. 인증 실패
```
❌ FAIL JWT 토큰 생성
   └─ 토큰 생성 실패: JWT_SECRET_KEY not found
```
**해결방법:**
- `.env` 파일에 JWT_SECRET_KEY 설정
- 환경 변수 로드 확인

#### 3. API 엔드포인트 오류
```
❌ FAIL 학생 목록 조회
   └─ HTTP 404
```
**해결방법:**
- API 엔드포인트 구현 확인
- 라우터 설정 확인
- 데이터베이스 연결 확인

#### 4. Celery 태스크 실패
```
❌ FAIL 학생 Excel 재생성 실패
   └─ 오류: Celery worker not running
```
**해결방법:**
- Celery 워커 실행 확인
- Redis 서버 연결 확인
- 태스크 큐 상태 확인

#### 5. AI API 오류
```
❌ FAIL AI 일반 채팅
   └─ HTTP 500: Gemini API key not found
```
**해결방법:**
- GEMINI_API_KEY 설정 확인
- API 키 유효성 확인
- 네트워크 연결 확인

## 🔧 문제 해결

### 일반적인 문제 해결

#### 1. 가상환경 문제
```bash
# 가상환경 재생성
cd backend
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. 의존성 문제
```bash
# 백엔드 의존성 재설치
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# 프론트엔드 의존성 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 3. 데이터베이스 문제
```bash
# 데이터베이스 마이그레이션
cd backend
alembic upgrade head

# 테스트 데이터 초기화
python init_test_data.py
```

#### 4. 포트 충돌 문제
```bash
# 포트 사용 확인
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 프로세스 종료
taskkill /PID <process_id> /F
```

### 로그 확인

#### 백엔드 로그
```bash
cd backend
# FastAPI 로그
tail -f logs/fastapi.log

# Celery 로그
tail -f logs/celery.log

# 애플리케이션 로그
tail -f logs/app.log
```

#### 프론트엔드 로그
```bash
cd frontend
# Next.js 로그
npm run dev 2>&1 | tee logs/nextjs.log

# 테스트 로그
npm test 2>&1 | tee logs/test.log
```

## 🎯 다음 단계

### 테스트 성공 후 진행사항

1. **실제 사용자 테스트**
   - 사용자 인터페이스 테스트
   - 사용자 경험 개선
   - 피드백 수집 및 반영

2. **성능 최적화**
   - API 응답 시간 최적화
   - 데이터베이스 쿼리 최적화
   - 프론트엔드 번들 크기 최적화

3. **보안 강화**
   - 입력 검증 강화
   - SQL 인젝션 방지
   - XSS 공격 방지
   - CSRF 토큰 구현

4. **모니터링 시스템**
   - 로그 수집 및 분석
   - 성능 모니터링
   - 오류 추적 및 알림

5. **프로덕션 배포**
   - Docker 컨테이너 배포
   - CI/CD 파이프라인 구축
   - 백업 및 복구 시스템

### 지속적인 테스트

- **자동화된 테스트**: GitHub Actions CI/CD
- **정기적인 테스트**: 일일/주간 테스트 실행
- **회귀 테스트**: 새로운 기능 추가 시 기존 기능 테스트
- **성능 테스트**: 정기적인 성능 벤치마크

## 📞 지원

테스트 실행 중 문제가 발생하면:

1. **로그 파일 확인**: 각 테스트의 상세 로그 확인
2. **환경 변수 확인**: 모든 필수 환경 변수 설정 확인
3. **의존성 확인**: 패키지 버전 호환성 확인
4. **문서 참조**: README.md 및 각 컴포넌트별 문서 확인

---

**마지막 업데이트**: 2024년 12월 1일
**버전**: 1.0.0 
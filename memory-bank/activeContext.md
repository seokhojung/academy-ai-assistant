# activeContext.md

## 현재 작업 및 집중 영역
- 백엔드/프론트엔드 기본 구조 구축 완료
- 학생 관리 API, JWT 인증 시스템 구현
- 실행 스크립트, Docker, .env 예시 제공
- 프론트엔드 대시보드/로그인/컴포넌트 라이브러리 구현
- firebase_admin 미설치로 인한 장애 즉시 해결(임시 코드 적용)
- **테스트 자동화 완료** (Jest + Testing Library + Playwright)
- **빌드/배포 자동화 완료** (Docker + CI/CD + 배포 스크립트)
- **2순위 UI 컴포넌트 구현 완료** (Glassmorphism KPI Cards, Skeleton Loader, Dark/Light Theme Toggle, Toast 알림 시스템)
- **프론트엔드 완전 안정화 완료** (구조 재설계, 의존성 충돌 해결, 환경 최적화)
- **백엔드-프론트엔드 연결 완료** (API 클라이언트 구현, 프록시 설정, 연결 테스트)
- **2순위 UI 컴포넌트 확장 완료** (AccentButton micro-interactions, 캘린더 컴포넌트, 차트 컴포넌트)
- **학생관리 페이지 Undo/Redo 기능 구현 완료** (편집 히스토리 관리, 키보드 단축키, 실시간 피드백)
- **Render 배포 환경 문제 해결 완료** (pydantic-settings 의존성 추가, 환경 변수 설정 개선)
- **프론트엔드 서브모듈 문제 완전 해결 완료** (서브모듈 흔적 제거, 일반 폴더로 복원, Git 정상화)
- **Vercel 배포 준비 완료** (frontend 폴더 GitHub 푸시 완료, Vercel 설정 가이드 준비)
- **JWT와 Firebase 역할 분석 완료** (이중 보안 시스템 구조, 인증 플로우, API 요청 플로우 문서화)

## 최근 변경 사항
- firebase_admin 등 누락 의존성 설치 및 인증 코드 임시 비활성화
- 서버 정상 기동 및 API 정상 동작 확인
- **프론트엔드 테스트 환경 구축 완료**:
  - Jest + Testing Library 설정
  - Playwright E2E 테스트 설정
  - 컴포넌트 단위 테스트 예제 추가
  - 테스트 자동화 스크립트 추가
- **빌드/배포 자동화 구축 완료**:
  - Docker 이미지 최적화 (멀티스테이지 빌드)
  - Docker Compose 전체 시스템 설정
  - Nginx 리버스 프록시 설정
  - GitHub Actions CI/CD 파이프라인
  - 자동화 배포 스크립트 (deploy.sh)
  - PostgreSQL + Redis 인프라 설정
- **2순위 UI 컴포넌트 구현 완료**:
  - Glassmorphism KPI Cards (프로젝트 개요 요구사항 충족)
  - Skeleton Loader (테이블 fetch 중 로딩)
  - Dark/Light Theme Toggle (완전한 테마 시스템)
  - Toast 알림 시스템 (Framer Motion 애니메이션 포함)
  - 학생 관리 페이지 생성 및 Skeleton Loader 적용
  - 강사 관리 페이지 Skeleton Loader 및 Toast 알림 적용
- **프론트엔드 완전 안정화 완료** (2025-01-27):
  - 완전한 환경 재설정 (모든 프로세스 종료, 포트 해제, 폴더 정리)
  - 구조 재설계 (React Query Provider 완전 분리, Layout 단순화)
  - 의존성 충돌 해결 (Next.js 15 + React 19 + @tanstack/react-query 호환성 확보)
  - 환경 최적화 (Next.js 설정 최적화, 포트 3001 고정, 성능 개선)
- **백엔드-프론트엔드 연결 완료** (2025-01-27):
  - 백엔드 서버 정상 실행 확인 (http://localhost:8000)
  - 프론트엔드 서버 정상 실행 확인 (http://localhost:3001)
  - API 클라이언트 구현 (중앙화된 API 통신, 에러 처리 개선)
  - 학생 API 연결 테스트 완료 (CRUD 작업 정상 동작)
  - 프록시 설정 최적화 (CORS 문제 해결)
- **2순위 UI 컴포넌트 확장 완료** (2025-01-27):
  - AccentButton micro-interactions (Framer Motion 호버/클릭 애니메이션)
  - 캘린더 컴포넌트 (수업 일정 관리, 이벤트 표시, 월별 네비게이션)
  - 차트 컴포넌트 (성적 통계, 출석률 추이, 다양한 차트 타입 지원)
  - 대시보드 통합 (캘린더 + 차트 섹션 추가, 실시간 데이터 시각화)
- **학생관리 페이지 Undo/Redo 기능 구현 완료** (2025-07-14):
  - 편집 히스토리 관리 시스템 구현 (EditHistory 인터페이스, 상태 관리)
  - Undo/Redo 버튼 UI 추가 (MUI IconButton, Tooltip, 비활성화 상태 표시)
  - 키보드 단축키 구현 (Ctrl+Z: Undo, Ctrl+Shift+Z: Redo)
  - 실시간 피드백 시스템 (토스트 메시지, 히스토리 상태 표시)
  - 백엔드 API 연동 (편집 취소/재실행 시 서버 데이터 동기화)
  - 히스토리 초기화 로직 (새 학생 등록, 삭제 시 히스토리 클리어)
- **학생관리 페이지 삭제 기능 개선 완료** (2025-07-14):
  - 행 선택 기능 완전 구현 (onRowSelectionModelChange 이벤트 연결)
  - 선택된 행 삭제 기능 개선 (백엔드 API 연동, 일괄 삭제)
  - 삭제 버튼 UI 개선 (선택된 행 개수 표시, 배지 표시)
  - 개별 행 삭제와 선택된 행 삭제 구분 (두 가지 삭제 방식 지원)
  - 삭제 후 상태 초기화 (선택 상태, 히스토리 클리어)
  - MUI Tooltip 경고 해결 (비활성화된 버튼을 span으로 감싸기)
  - 행 선택 데이터 형식 처리 개선 (Set 객체를 배열로 변환)
  - API 클라이언트 응답 처리 개선 (빈 JSON 응답 처리)
  - 삭제 기능 완전 구현 (소프트 삭제, 활성 학생만 표시)
- **학생관리 페이지 데이터 저장 문제 해결 완료** (2025-07-14):
  - 행 추가 기능 백엔드 연동 (새 학생 생성 API 호출)
  - 컬럼 추가/삭제/편집 로컬 스토리지 저장 (새로고침 후에도 유지)
  - 새 학생 등록 폼 검증 강화 (필수 필드 검증, 에러 메시지 개선)
  - 데이터 일관성 확보 (모든 CRUD 작업이 백엔드와 동기화)
  - API 에러 처리 개선 (422 오류 시 상세 에러 메시지 표시)
  - 데이터 타입 변환 수정 (tuition_fee를 float로, tuition_due_date를 ISO 문자열로)
- **Render 배포 환경 문제 해결 완료** (2025-07-14):
  - pydantic_settings 모듈 누락으로 인한 배포 실패 해결
  - requirements.txt에 pydantic-settings==2.0.3 추가
  - 환경 변수 기반 설정 시스템으로 전환 (os.getenv 사용)
  - Render 배포 가이드 문서 생성 (RENDER_DEPLOYMENT.md)
  - 배포 환경 호환성 확보 및 안정성 향상
- **프론트엔드 서브모듈 문제 완전 해결 완료** (2025-01-27):
  - 서브모듈 흔적 완전 제거 (.gitmodules, .git/config, .git/modules/frontend 삭제)
  - frontend 폴더 백업 및 복원 (일반 폴더로 정상화)
  - Git 상태 정리 (서브모듈 관련 커밋 정리)
  - frontend 폴더 Git 추가 및 커밋 (63개 파일, 20,124줄 추가)
  - GitHub 푸시 완료 (Vercel 배포 준비 완료)
  - 비밀키 파일 보안 처리 (.gitignore에 추가)

## 다음 단계
- **Vercel 프론트엔드 배포 완료** (Root Directory: frontend 설정)
- **Render 백엔드 배포 상태 확인** (환경 변수 설정 확인)
- **프론트엔드-백엔드 연결 테스트** (프로덕션 환경에서 API 연결)
- **3순위 고급 기능** (Excel 미리보기 컴포넌트, QR 코드 컴포넌트, Drag & Drop 파일 업로드)
- **백엔드 3순위 개선** (PostgreSQL 전환, 모니터링, 고급 보안)
- Firebase Admin 연동 및 실제 인증 완성
- Gemini API, 강사/교재/AI 채팅 등 미구현 기능 설계/구현
- 메모리뱅크(progress.md 등) 최신화
- **프로덕션 환경 실제 배포 및 모니터링**

## 주요 이슈/결정 사항
- 인증 시스템은 JWT 기반으로 정상 동작, Firebase 연동은 임시 중단
- 프론트엔드 권한 경고는 서비스 동작에 영향 없음
- 1주차 목표 대비 약 95% 진행, 장애 즉시 해결 가능
- **테스트 커버리지 기준**: 70% (branches, functions, lines, statements)
- **배포 환경**: Docker 컨테이너 + Nginx 리버스 프록시 + PostgreSQL + Redis
- **프론트엔드 완전 안정화 완료**: 구조 재설계, 의존성 충돌 해결, 환경 최적화로 안정성 확보
- **백엔드-프론트엔드 연결 완료**: API 클라이언트 구현으로 안정적인 통신 확보
- **2순위 UI 컴포넌트 확장 완료**: micro-interactions, 캘린더, 차트로 사용자 경험 향상
- **Undo/Redo 기능 완료**: 편집 히스토리 관리, 키보드 단축키, 실시간 피드백으로 사용자 편의성 대폭 향상
- **프론트엔드 서브모듈 문제 완전 해결**: 서브모듈 흔적 제거, 일반 폴더로 복원, Git 정상화로 Vercel 배포 준비 완료
- **JWT와 Firebase 이중 보안 시스템**: JWT는 API 보안, Firebase는 사용자 인증을 담당하는 협력 관계 구축

## 실행/개발/배포 규칙 (2025-01-27 최신)

### 1. 백엔드 실행 방법
- 반드시 backend 폴더에서 아래 순서로 실행
- 가상환경 자동화: start-backend.bat 사용 권장
- 수동 실행 시:
  1. cd backend
  2. venv\Scripts\activate.bat
  3. set PYTHONPATH=./app
  4. python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
- reload 시에도 PYTHONPATH=./app 환경변수 반드시 유지

### 2. 의존성 관리
- 모든 의존성은 backend/requirements.txt에 명시
- venv 활성화 후 pip install -r requirements.txt로 설치
- 패키지 추가/업데이트 시 pip freeze > requirements.txt로 동기화

### 3. 폴더/모듈 구조
- backend/app/ 하위에 api, core, models, services 등 계층화
- FastAPI 앱 엔트리포인트: app/main.py
- 모든 import는 절대경로(app.XXX) 사용, PYTHONPATH로 경로 보장

### 4. 환경변수 관리
- .env 파일 또는 시스템 환경변수로 관리
- 필수 환경변수: PYTHONPATH, DATABASE_URL, FIREBASE_*, GCS_*, 등

### 5. 실행 스크립트 일관성
- start-backend.bat에서 venv, PYTHONPATH, 서버 실행까지 자동화
- reload, 배포, 테스트 등 모든 환경에서 동일하게 동작하도록 유지

### 6. 문서화
- 위 규칙을 memory-bank/activeContext.md, systemPatterns.md, techContext.md에 항상 최신화 

## 프론트엔드 실행/개발/배포 규칙 (2025-01-27 최신)

### 1. 실행 방법
- 반드시 frontend 폴더에서 아래 순서로 실행
- 자동화: start-frontend.bat 사용 권장 (환경 체크 + 자동 설치 포함)
- 수동 실행 시:
  1. cd frontend
  2. npm install (최초 1회)
  3. npm run dev (3001번 포트 고정, 안정화 완료)
- 환경변수는 .env 파일로 관리, .env.example 참고

### 2. 폴더/컴포넌트 구조
- app/: Next.js App Router 라우트
- app/providers/: Client Component Provider (React Query 등)
- src/components/: UI, 인증 등 컴포넌트 분리
- lib/: 유틸리티, firebase 연동, API 클라이언트 등
- public/: 정적 리소스

### 3. 의존성 관리
- package.json, package-lock.json으로 관리
- 패키지 추가/업데이트 시 npm install, npm update 사용
- Next.js 15 + React 19 + @tanstack/react-query 호환성 유지

### 4. 환경변수 관리
- NEXT_PUBLIC_API_URL, NEXT_PUBLIC_FIREBASE_* 등 .env로 관리
- .env.example 파일 제공

### 5. 개발 품질 관리 (자동화 적용 완료)
- npm run lint:fix: 코드 품질 자동 수정
- npm run type-check: TypeScript 타입 검사
- npm run setup: 초기 설정 자동화
- npm run check: 타입 검사 + 코드 품질 검사

### 6. 테스트 자동화 (3순위 완료)
- **단위 테스트**: Jest + Testing Library
  - npm test: 모든 테스트 실행
  - npm run test:watch: 감시 모드
  - npm run test:coverage: 커버리지 리포트
- **E2E 테스트**: Playwright
  - npm run test:e2e: 모든 E2E 테스트
  - npm run test:e2e:ui: UI 모드
  - npm run test:e2e:headed: 브라우저 창 모드
- **전체 테스트**: npm run test:all (단위 + E2E)
- **CI 테스트**: npm run test:ci (커버리지 포함)

### 7. 빌드/배포 자동화 (4순위 완료)
- **Docker 이미지**: 멀티스테이지 빌드로 최적화
  - npm run docker:build: 로컬 Docker 이미지 빌드
  - npm run docker:run: 로컬 Docker 컨테이너 실행
  - npm run docker:push: 레지스트리에 이미지 푸시
- **빌드 최적화**:
  - npm run analyze: 번들 분석
  - npm run export: 정적 내보내기
  - npm run clean: 빌드 캐시 정리
- **CI/CD**: GitHub Actions 파이프라인
  - 자동 테스트 및 빌드
  - Docker 이미지 자동 푸시
  - 스테이징/프로덕션 자동 배포

### 8. 문서화/온보딩 (개선 완료)
- README.md에 실행/개발 규칙, 환경변수 설명 등 구체화
- memory-bank/activeContext.md, systemPatterns.md, techContext.md에 항상 최신화

### 9. 자동화 적용 현황 (2025-01-27)
- ✅ start-frontend.bat: 환경 체크 + 자동 설치 + .env 파일 체크
- ✅ package.json: 개발 품질 관리 스크립트 추가
- ✅ README.md: 온보딩/개발 규칙 구체화
- ✅ **테스트 자동화 완료**: Jest + Testing Library + Playwright
- ✅ **빌드/배포 자동화 완료**: Docker + CI/CD + 배포 스크립트
- ✅ **프론트엔드 완전 안정화 완료**: 구조 재설계, 의존성 충돌 해결, 환경 최적화
- ✅ **백엔드-프론트엔드 연결 완료**: API 클라이언트 구현, 프록시 설정, 연결 테스트
- ✅ **2순위 UI 컴포넌트 확장 완료**: micro-interactions, 캘린더, 차트 컴포넌트

## 배포 환경 규칙 (2025-01-27 최신)

### 1. Docker 환경
- **전체 시스템**: docker-compose.yml로 관리
- **백엔드**: Python 3.11 + FastAPI + PostgreSQL + Redis
- **프론트엔드**: Node.js 18 + Next.js + Nginx
- **인프라**: PostgreSQL 15 + Redis 7 + Nginx

### 2. 배포 자동화
- **배포 스크립트**: deploy.sh로 모든 배포 과정 자동화
- **환경별 배포**: production/staging 환경 분리
- **백업/롤백**: 자동 백업 및 롤백 기능
- **헬스 체크**: 모든 서비스 상태 자동 모니터링

### 3. CI/CD 파이프라인
- **GitHub Actions**: 자동 테스트 → 빌드 → 배포
- **보안 스캔**: Trivy를 통한 취약점 검사
- **커버리지**: 테스트 커버리지 자동 리포트
- **다중 환경**: develop → staging → main → production

### 4. 모니터링 및 로그
- **헬스 체크**: /health 엔드포인트로 서비스 상태 확인
- **로그 관리**: Docker 로그 자동 수집 및 관리
- **성능 모니터링**: Nginx 액세스 로그 및 백엔드 로그 분석 
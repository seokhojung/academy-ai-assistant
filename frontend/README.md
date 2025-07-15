# Academy AI Assistant - Frontend

Next.js 14 기반의 학원 운영 시스템 프론트엔드입니다.

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 의존성 설치
npm install

# 환경변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 환경변수를 설정하세요
```

### 2. 개발 서버 실행
```bash
# 자동화 스크립트 사용 (권장)
start-frontend.bat

# 또는 수동 실행
npm run dev
```

서버가 http://localhost:3002 에서 실행됩니다.

## 🧪 테스트

### 단위 테스트 (Jest + Testing Library)
```bash
# 모든 테스트 실행
npm test

# 테스트 감시 모드
npm run test:watch

# 커버리지 리포트와 함께 테스트 실행
npm run test:coverage
```

### E2E 테스트 (Playwright)
```bash
# 모든 E2E 테스트 실행
npm run test:e2e

# UI 모드로 E2E 테스트 실행
npm run test:e2e:ui

# 브라우저 창을 열고 E2E 테스트 실행
npm run test:e2e:headed
```

### 전체 테스트
```bash
# 단위 테스트 + E2E 테스트 모두 실행
npm run test:all

# CI 환경용 테스트 (커버리지 포함)
npm run test:ci
```

## 📁 프로젝트 구조

```
frontend/
├── app/                    # Next.js App Router
│   ├── dashboard/         # 대시보드 페이지
│   ├── students/          # 학생 관리 페이지
│   ├── teachers/          # 강사 관리 페이지
│   ├── materials/         # 교재 관리 페이지
│   └── ai-chat/           # AI 채팅 페이지
├── src/
│   └── components/        # React 컴포넌트
│       ├── ui/            # 기본 UI 컴포넌트
│       ├── auth/          # 인증 관련 컴포넌트
│       └── __tests__/     # 컴포넌트 테스트
├── lib/                   # 유틸리티 및 설정
├── public/                # 정적 리소스
├── e2e/                   # E2E 테스트
├── __mocks__/             # Jest 모크 파일
├── jest.config.ts         # Jest 설정
├── jest.setup.ts          # Jest 환경 설정
├── playwright.config.ts   # Playwright 설정
└── package.json
```

## 🛠️ 개발 도구

### 코드 품질 관리
```bash
# 코드 품질 검사
npm run lint

# 코드 품질 자동 수정
npm run lint:fix

# TypeScript 타입 검사
npm run type-check

# 전체 검사 (타입 + 린트)
npm run check
```

### 초기 설정
```bash
# 프로젝트 초기 설정 (의존성 설치 + 코드 품질 수정)
npm run setup
```

## 🔧 환경변수

`.env` 파일에서 다음 환경변수들을 설정하세요:

```env
# API 설정
NEXT_PUBLIC_API_URL=http://localhost:8000

# Firebase 설정
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_auth_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_storage_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

## 📊 테스트 커버리지

테스트 커버리지는 다음 기준을 만족해야 합니다:
- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%
- **Statements**: 70%

커버리지 리포트는 `coverage/` 폴더에 생성됩니다.

## 🎯 테스트 전략

### 단위 테스트
- **컴포넌트 테스트**: React 컴포넌트의 렌더링과 상호작용
- **유틸리티 테스트**: 헬퍼 함수들의 로직 검증
- **모킹**: 외부 의존성(API, 라우터 등) 모킹

### E2E 테스트
- **페이지 네비게이션**: 주요 페이지 간 이동
- **사용자 플로우**: 실제 사용자 시나리오
- **반응형 디자인**: 다양한 화면 크기에서의 동작
- **크로스 브라우저**: Chrome, Firefox, Safari 지원

## 🚀 배포

```bash
# 프로덕션 빌드
npm run build

# 프로덕션 서버 실행
npm start
```

## 📝 개발 규칙

1. **컴포넌트 작성 시**: 반드시 테스트 파일도 함께 작성
2. **새 기능 추가 시**: 관련 E2E 테스트 추가
3. **코드 변경 시**: `npm run test:all`로 전체 테스트 실행
4. **커밋 전**: `npm run check`로 코드 품질 확인

## 🔗 관련 링크

- [Next.js 문서](https://nextjs.org/docs)
- [Jest 문서](https://jestjs.io/docs/getting-started)
- [Testing Library 문서](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright 문서](https://playwright.dev/docs/intro)

# Vercel 배포 가이드

## 1. Vercel 계정 생성 및 프로젝트 연결

### 1.1 Vercel 계정 생성
1. https://vercel.com 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭

### 1.2 GitHub 저장소 연결
1. GitHub 저장소 선택: `seokhojung/academy-ai-assistant`
2. Framework Preset: `Next.js` 자동 감지
3. Root Directory: `frontend` (프론트엔드 폴더)
4. "Deploy" 클릭

## 2. 환경 변수 설정

### 2.1 Vercel 대시보드에서 설정
1. 프로젝트 대시보드 → Settings → Environment Variables
2. 다음 환경 변수 추가:

```
NEXT_PUBLIC_API_URL=https://academy-ai-assistant.onrender.com
```

### 2.2 실제 Render URL로 변경
- `your-render-app.onrender.com`을 실제 Render 배포 URL로 변경
- 예: `academy-ai-assistant.onrender.com`
- **중요**: URL 끝에 `/api`를 추가하지 마세요. 프론트엔드에서 자동으로 추가합니다.

## 3. 배포 설정

### 3.1 빌드 설정
- Framework: Next.js
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`

### 3.2 도메인 설정
- Vercel에서 자동으로 제공하는 도메인 사용
- 예: `academy-ai-assistant.vercel.app`
- 커스텀 도메인 연결 가능

## 4. 배포 후 확인사항

### 4.1 배포 성공 확인
- Vercel 대시보드에서 배포 상태 확인
- 제공된 URL로 접속 테스트

### 4.2 API 연결 테스트
- 브라우저에서 프론트엔드 접속
- 학생 관리 페이지에서 데이터 로딩 확인
- 네트워크 탭에서 API 호출 확인

### 4.3 CORS 설정 확인
- 백엔드(Render)에서 프론트엔드(Vercel) 도메인 허용
- Render 대시보드에서 CORS 설정 업데이트

## 5. 자동 배포 설정

### 5.1 GitHub 연동
- GitHub 저장소에 푸시하면 자동 배포
- 브랜치별 배포 설정 가능
- Preview 배포 지원

### 5.2 환경별 배포
- Production: `main` 브랜치
- Preview: `develop` 브랜치
- 각 환경별 환경 변수 설정 가능

## 6. 문제 해결

### 6.1 빌드 실패
- Node.js 버전 확인 (18.x 이상 권장)
- 의존성 설치 오류 확인
- TypeScript 오류 확인

### 6.2 API 연결 실패
- 환경 변수 `NEXT_PUBLIC_API_URL` 확인
- Render 백엔드 서버 상태 확인
- CORS 설정 확인

### 6.3 CORS 오류 해결
- Vercel 환경 변수 `NEXT_PUBLIC_API_URL=https://academy-ai-assistant.onrender.com` 설정
- 프론트엔드 재배포
- 브라우저 캐시 삭제
- Render 백엔드에서 Vercel 도메인 허용 확인

### 6.3 성능 최적화
- Vercel Analytics 활성화
- 이미지 최적화 설정
- 번들 크기 최적화

## 7. 모니터링 및 분석

### 7.1 Vercel Analytics
- 페이지 뷰, 성능 메트릭 확인
- 사용자 행동 분석
- 성능 최적화 인사이트

### 7.2 로그 확인
- Function Logs에서 서버 로그 확인
- 에러 추적 및 디버깅
- 성능 병목 지점 파악

## 8. 보안 설정

### 8.1 환경 변수 보안
- 민감한 정보는 환경 변수로 관리
- API 키, 비밀번호 등 노출 금지
- Vercel 대시보드에서 안전하게 관리

### 8.2 HTTPS 강제
- Vercel에서 자동 HTTPS 제공
- HTTP → HTTPS 리다이렉트 설정
- 보안 헤더 자동 설정 
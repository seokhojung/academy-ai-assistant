# Academy AI Assistant - 프로젝트 개요

## 프로젝트 정보
- **프로젝트명**: Academy AI Assistant
- **목적**: Excel 기반 학원 운영 시스템을 **FastAPI + PostgreSQL** API와 **Next.js 14** 프론트로 재구축하고, **Gemini 1.5 Flash 무료 API** + **Excel Rebuilder** 구조로 자연어로 학생·강사·교재 데이터를 관리·파일 자동 재생성·버전 관리를 통합한다.

## 핵심 가치 제안
- **자연어 기반 데이터 관리**: AI를 통한 직관적인 학생·강사·교재 정보 관리
- **Excel 자동 재생성**: 데이터 변경 시 Excel 파일 자동 업데이트 및 버전 관리
- **모바일 친화적 PWA**: QR 체크인, 교재 바코드 스캔, 오프라인 지원
- **실시간 대시보드**: 학생·수강료·교재 통계 및 시각화

## 3단계 개발 계획

### 1단계 - 프로젝트 기초 구축 (4주)
- FastAPI 스켈레톤, SQLite 모델 정의
- Next.js 초기화, 로그인 페이지
- Gemini 통합, 자연어 파서, JWT
- 학생·강사 페이지 및 채팅 UI
- 교재 API, Excel Rebuilder CLI, SSE
- Resources 탭 + Excel 미리보기
- Role-ACL, PITR 설정, 보안 헤더
- 대시보드, 모바일 PWA, Undo/Redo

### 2단계 - MVP 구축 & 프로덕트 검증 (4주)
- 베타 오픈 → 20명 내부 테스트 2주
- 성공 KPI:
  - 자연어 명령 ≥ 300건, 처리 성공률 ≥ 92%
  - 데이터 오류 0건, P95 응답 < 700ms, 가동률 99.9%
  - 파일 업·다운 100%, 프리뷰 TTFB < 800ms

### 3단계 - UI Glow-Up & Storybook (3주)
- Glassmorphism KPI Cards
- AccentButton micro-interactions (Framer Motion)
- Skeleton Loader during table fetch
- Dark / Light theme toggle
- Storybook Design System
- Chromatic visual regression CI

## 주요 기능 목록
1. **AI 자연어 관리** — 학생·강사·교재 CRUD
2. **파일 관리 & Excel Rebuilder** — 업·다운·삭제·메타데이터 + 자동 재생성
3. **Excel 미리보기** — SheetJS → Handsontable 100-row chunk
4. **대시보드** — 학생·수강료·교재 통계 카드 & 그래프
5. **모바일 PWA** — QR 체크인·교재 바코드 스캔·파일 뷰

## 예상 페이지 구성
- `/login` — Google Auth
- `/dashboard` — 통계 카드·Recharts (GlassCard)
- `/students` — 테이블 + AI 채팅 + SkeletonRows
- `/teachers` — 강의 스케줄 캘린더 + AI 채팅 + AccentButton
- `/materials` — 교재 테이블 + 임계치 설정
- `/resources` — Drag&Drop 업로드·목록
- `/resources/[id]/preview` — Excel 미리보기

## 외부 연동 요소
- Gemini 1.5 Flash API
- Firebase Auth
- GCS presigned URL
- GitHub Actions → Cloud Build → Cloud Run (Blue/Green)

## 제한사항
- 전송·저장 모두 TLS/암호화
- Budget Alert USD 10/월
- Excel Rebuilder 실패율 < 0.1% (Retry 3회)

## 과금 전략
- **베타**: 무료 (기간제한 1개월)
- **런칭**: ₩29,000/월 (학생 ≤200·강사 ≤20)
- **Growth**: ₩59,000/월 (무제한 + 우선지원) 
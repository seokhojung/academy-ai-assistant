# Academy AI Assistant - 기술 컨텍스트

## 기술 스택 상세

### AI Layer
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **Gemini 1.5 Flash** | google-generativeai v0.5 | Streaming, 60 req/min 무료 | 자연어 명령 파싱 및 처리 |
| **Natural Language Parser** | Custom | JSON Schema 기반 | 자연어를 구조화된 데이터로 변환 |

### Backend Layer
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **FastAPI** | 0.111 | Async, OpenAPI docs | REST API 서버 |
| **Uvicorn** | Latest | ASGI 서버 | FastAPI 실행 환경 |
| **Pydantic** | v2 | 데이터 검증 | 요청/응답 모델 검증 |
| **SQLModel** | Latest | ORM | 데이터베이스 모델 및 쿼리 |
| **Alembic** | Latest | 마이그레이션 | 데이터베이스 스키마 관리 |

### Database Layer
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **PostgreSQL** | 15 | PITR 활성화, row-level lock | 프로덕션 데이터베이스 |
| **SQLite** | 3.x | 개발용 | 로컬 개발 환경 |
| **Redis** | 7 | LRU 256MB, JWT 블랙리스트 | 캐시 및 세션 관리 |

### Worker Layer
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **Celery** | 5 | Redis broker | 비동기 태스크 큐 |
| **openpyxl** | Latest | write_only 모드 | Excel 파일 생성 |
| **portalocker** | Latest | 파일 잠금 | Excel 쓰기 충돌 방지 |

### Frontend Layer
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **Next.js** | 14 | App Router, RSC | React 프레임워크 |
| **TypeScript** | 5 | 엄격 모드 | 타입 안전성 |
| **Tailwind CSS** | 3.4 | JIT 컴파일러 | 스타일링 |
| **tRPC** | Latest | 타입 안전 API | 클라이언트-서버 통신 |
| **TanStack Query** | Latest | 서버 상태 관리 | 데이터 페칭 및 캐싱 |

### UI Components
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **shadcn/ui** | Latest | Radix UI 기반 | 재사용 가능한 컴포넌트 |
| **Handsontable** | 9 | 100행 청크 | Excel 미리보기 |
| **SheetJS** | Latest | XLSX 파싱 | Excel 파일 읽기 |
| **Framer Motion** | Latest | 마이크로 인터랙션 | 애니메이션 |
| **Recharts** | Latest | 데이터 시각화 | 대시보드 차트 |

### Authentication
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **Firebase Auth** | Latest | Google Sign-In | 사용자 인증 |
| **JWT** | PyJWT | 15분 액세스, 7일 리프레시 | 토큰 기반 인증 |

### Storage
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **Google Cloud Storage** | Latest | Versioning ON, Glacier lifecycle | 파일 저장소 |
| **Presigned URL** | Custom | 직접 업로드/다운로드 | 브라우저 직접 접근 |

### Real-time Communication
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **Server-Sent Events** | Native | `/stream/chat`, `/stream/files` | 실시간 스트리밍 |

### DevOps & Monitoring
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **GitHub Actions** | Latest | CI/CD 파이프라인 | 자동화 |
| **Google Cloud Build** | Latest | Docker 이미지 빌드 | 컨테이너 빌드 |
| **Google Cloud Run** | Latest | Blue/Green 배포 | 서버리스 배포 |
| **Sentry** | Latest | 에러 추적 | 모니터링 |
| **Grafana** | Latest | 메트릭 시각화 | 대시보드 |

### Testing
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **pytest** | Latest | 단위 테스트 | 백엔드 테스트 |
| **Playwright** | Latest | E2E 테스트 | 전체 플로우 테스트 |
| **k6** | Latest | 부하 테스트 | 성능 테스트 |

### Development Tools
| 기술 | 버전 | 설정 | 용도 |
|------|------|------|------|
| **Storybook** | Latest | 컴포넌트 문서화 | UI 개발 |
| **Chromatic** | Latest | 시각적 회귀 테스트 | UI 테스트 |
| **ESLint** | Latest | 코드 품질 | 린팅 |
| **Prettier** | Latest | 코드 포맷팅 | 포맷팅 |

## 개발 환경 설정

### 필수 요구사항
- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 15+
- **Redis**: 7+
- **Docker**: 최신 버전

### 환경 변수
```bash
# AI
GEMINI_API_KEY=your_gemini_api_key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/academy_ai
REDIS_URL=redis://localhost:6379

# Auth
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email

# Storage
GCS_BUCKET_NAME=your_bucket_name
GCS_CREDENTIALS=path/to/credentials.json

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_CONFIG=your_firebase_config
```

### 로컬 개발 설정
1. **백엔드 실행**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **프론트엔드 실행**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Worker 실행**
   ```bash
   cd backend
   celery -A app.workers.celery worker --loglevel=info
   ```

## 성능 최적화

### 백엔드 최적화
- **Connection Pooling**: 데이터베이스 연결 풀 관리
- **Redis 캐싱**: 자주 접근하는 데이터 캐싱
- **비동기 처리**: Celery를 통한 백그라운드 작업
- **SSE 스트리밍**: 실시간 데이터 전송

### 프론트엔드 최적화
- **Next.js RSC**: 서버 컴포넌트를 통한 성능 향상
- **TanStack Query**: 서버 상태 캐싱 및 동기화
- **Code Splitting**: 동적 임포트를 통한 번들 최적화
- **Image Optimization**: Next.js 이미지 최적화

### 데이터베이스 최적화
- **인덱싱**: 자주 조회되는 컬럼 인덱스 생성
- **쿼리 최적화**: N+1 문제 방지
- **PITR**: Point-in-Time Recovery 설정

## 보안 설정

### 인증 보안
- **JWT 토큰**: 짧은 만료 시간 (15분)
- **리프레시 토큰**: 안전한 갱신 메커니즘
- **Firebase Auth**: Google의 보안 인프라 활용

### 데이터 보안
- **TLS 암호화**: 모든 통신 암호화
- **GCS 버전 관리**: 파일 변경 이력 추적
- **Row-level Lock**: 데이터베이스 수준 잠금

### API 보안
- **Rate Limiting**: API 요청 제한
- **CORS 설정**: 허용된 도메인만 접근
- **Input Validation**: 모든 입력 데이터 검증 
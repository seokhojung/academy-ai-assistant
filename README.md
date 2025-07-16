# Academy AI Assistant

학원 운영을 위한 AI 기반 관리 시스템입니다.

## 🚀 빠른 시작

### 개발 환경 실행

```bash
# 백엔드 실행
cd backend
start-backend.bat

# 프론트엔드 실행 (새 터미널)
cd frontend
start-frontend.bat
```

### Docker 환경 실행

```bash
# 전체 시스템 실행
docker-compose up -d

# 특정 서비스만 실행
docker-compose up -d backend frontend
```

## 🏗️ 프로젝트 구조

```
Academy-AI-Assistant/
├── backend/                 # FastAPI 백엔드
│   ├── app/                # 애플리케이션 코드
│   ├── venv/               # Python 가상환경
│   ├── requirements.txt    # Python 의존성
│   ├── Dockerfile          # 백엔드 Docker 설정
│   └── start-backend.bat   # 백엔드 실행 스크립트
├── frontend/               # Next.js 프론트엔드
│   ├── app/                # Next.js App Router
│   ├── src/                # React 컴포넌트
│   ├── package.json        # Node.js 의존성
│   ├── Dockerfile          # 프론트엔드 Docker 설정
│   └── start-frontend.bat  # 프론트엔드 실행 스크립트
├── nginx/                  # Nginx 설정
│   └── nginx.conf          # 리버스 프록시 설정
├── docker-compose.yml      # 전체 시스템 Docker 설정
├── deploy.sh               # 배포 자동화 스크립트
└── README.md               # 프로젝트 문서
```

## 🧪 테스트

### 단위 테스트
```bash
# 프론트엔드 테스트
cd frontend
npm test

# 백엔드 테스트
cd backend
pytest
```

### E2E 테스트
```bash
# 프론트엔드 E2E 테스트
cd frontend
npm run test:e2e
```

## 🚀 배포

### 자동 배포 (권장)
```bash
# 프로덕션 배포
./deploy.sh production

# 스테이징 배포
./deploy.sh staging
```

### 수동 배포
```bash
# Docker 이미지 빌드
docker-compose build

# 서비스 시작
docker-compose up -d

# 상태 확인
docker-compose ps
```

### 배포 스크립트 옵션
```bash
./deploy.sh deploy    # 배포
./deploy.sh rollback  # 롤백
./deploy.sh backup    # 백업
./deploy.sh health    # 헬스 체크
./deploy.sh logs      # 로그 확인
./deploy.sh stop      # 서비스 중지
./deploy.sh start     # 서비스 시작
./deploy.sh restart   # 서비스 재시작
```

## 🔧 환경 설정

### 환경변수

#### 백엔드 (.env)
```env
DATABASE_URL=postgresql://academy_user:academy_password@localhost:5432/academy_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
FIREBASE_PROJECT_ID=your-firebase-project-id
GEMINI_API_KEY=your-gemini-api-key
```

#### 프론트엔드 (.env)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-firebase-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=your-firebase-app-id
```

## 📊 모니터링

### 헬스 체크
```bash
# 전체 시스템 헬스 체크
curl http://localhost/health

# 개별 서비스 헬스 체크
curl http://localhost:8000/health  # 백엔드
curl http://localhost:3000         # 프론트엔드
```

### 로그 확인
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🔒 보안

### SSL/TLS 설정
1. SSL 인증서를 `nginx/ssl/` 디렉토리에 배치
2. `nginx/nginx.conf`에서 HTTPS 설정 주석 해제
3. 도메인 설정 업데이트

### 방화벽 설정
```bash
# 필요한 포트만 열기
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 22/tcp   # SSH
```

## 🚨 문제 해결

### 일반적인 문제

#### 백엔드 연결 오류
```bash
# 데이터베이스 연결 확인
docker-compose exec postgres psql -U academy_user -d academy_db

# Redis 연결 확인
docker-compose exec redis redis-cli ping
```

#### 프론트엔드 빌드 오류
```bash
# 캐시 정리
cd frontend
npm run clean
npm install
npm run build
```

#### Docker 컨테이너 문제
```bash
# 컨테이너 재시작
docker-compose restart

# 이미지 재빌드
docker-compose build --no-cache
docker-compose up -d
```

## 📈 성능 최적화

### 프론트엔드 최적화
```bash
# 번들 분석
cd frontend
npm run analyze

# 정적 내보내기
npm run export
```

### 백엔드 최적화
```bash
# 데이터베이스 인덱스 확인
docker-compose exec postgres psql -U academy_user -d academy_db -c "\d+"

# Redis 캐시 확인
docker-compose exec redis redis-cli info memory
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해 주세요.

---

**Academy AI Assistant** - 학원 운영의 미래를 만들어갑니다 🎓 "# Trigger redeploy" 

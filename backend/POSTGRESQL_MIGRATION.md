# PostgreSQL 마이그레이션 가이드

## 개요
SQLite에서 PostgreSQL로 데이터베이스를 마이그레이션하는 방법을 안내합니다.

## 사전 준비

### 1. PostgreSQL 데이터베이스 생성 (Render)
1. Render 대시보드에서 "New" → "PostgreSQL" 클릭
2. 데이터베이스 이름: `academy_db`
3. 사용자 이름: `academy_user`
4. 지역: Oregon (US West)
5. PostgreSQL 버전: 16
6. "Create Database" 클릭

### 2. 환경 변수 설정
1. `academy-ai-assistant` 서비스 클릭
2. "Environment" → "Environment Variables" 클릭
3. 기존 SQLite `DATABASE_URL` 삭제
4. 새로운 PostgreSQL `DATABASE_URL` 추가:
   ```
   DATABASE_URL=postgresql://academy_user:비밀번호@호스트:포트/academy_db
   ```

## 마이그레이션 단계

### 1. 로컬에서 마이그레이션 실행
```bash
cd backend
python migrate_to_postgresql.py
```

### 2. 연결 테스트
```bash
python test_postgresql_connection.py
```

### 3. 서비스 재배포
Render 대시보드에서 "Manual Deploy" 클릭

## 마이그레이션 스크립트 설명

### migrate_to_postgresql.py
- SQLite 데이터를 JSON으로 백업
- PostgreSQL로 데이터 이전
- 모든 테이블 (user, teacher, student, material) 마이그레이션

### test_postgresql_connection.py
- PostgreSQL 연결 테스트
- 환경 변수 확인
- 테이블 생성 테스트

## 주의사항

### 1. 데이터 백업
- 마이그레이션 전 반드시 기존 데이터 백업
- JSON 백업 파일이 자동으로 생성됨

### 2. 환경 변수
- `DATABASE_URL`이 PostgreSQL 형식으로 변경됨
- 기존 SQLite URL은 삭제해야 함

### 3. 의존성
- `psycopg2-binary==2.9.7`이 requirements.txt에 포함됨

## 문제 해결

### 연결 오류
1. 환경 변수 확인
2. PostgreSQL 서비스 상태 확인
3. 방화벽 설정 확인

### 데이터 손실
1. JSON 백업 파일 확인
2. 수동으로 데이터 복원

### 성능 이슈
1. 연결 풀 설정 확인
2. 인덱스 생성 확인

## 롤백 방법

### SQLite로 되돌리기
1. 환경 변수에서 PostgreSQL URL 삭제
2. SQLite URL 추가: `sqlite:///./academy_ai.db`
3. 서비스 재배포

## 성능 최적화

### PostgreSQL 설정
- 연결 풀 크기 조정
- 인덱스 최적화
- 쿼리 성능 모니터링

### 애플리케이션 설정
- 세션 관리 최적화
- 캐싱 전략 적용
- 배치 처리 구현 
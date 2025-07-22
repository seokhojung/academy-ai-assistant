# AI 챗봇 지침 시스템

## 📁 디렉토리 구조
```
backend/app/ai/
├── core/           # 핵심 지침 컴포넌트
│   ├── base_prompt.py          # 기본 지침 정의
│   ├── context_builder.py      # 컨텍스트 데이터 빌더
│   └── response_validator.py   # 응답 검증 시스템
├── adapters/       # AI 모델별 어댑터
│   ├── base_adapter.py         # AI 어댑터 인터페이스
│   ├── gemini_adapter.py       # Gemini 어댑터
│   ├── openai_adapter.py       # OpenAI 어댑터
│   └── adapter_factory.py      # 어댑터 팩토리
├── services/       # 통합 서비스
│   ├── unified_ai_service.py   # 통합 AI 서비스
│   └── ai_service_factory.py   # 서비스 팩토리
└── utils/          # 유틸리티
```

## 🎯 핵심 지침
1. **실제 데이터 사용 강제**: 제공된 데이터베이스 데이터만 사용, 가짜 데이터 생성 금지
2. **JSON 형식 응답 강제**: HTML, 마크다운, 일반 텍스트 절대 사용 금지
3. **요청한 데이터만 포함**: 요청하지 않은 데이터는 절대 포함하지 않음
4. **정확한 수치 사용**: 제공된 정확한 수치만 사용

## 🔄 모델 변경 방법
1. 환경변수 수정: `AI_MODEL=openai` 또는 `AI_MODEL=gemini`
2. API 키 설정: `OPENAI_API_KEY=your-key` 또는 `GEMINI_API_KEY=your-key`
3. 서버 재시작: `start-backend.bat`

## 🧪 테스트 방법
```bash
cd backend
python test_new_ai_system.py
```

## 📊 모니터링
- 응답 검증 로그 확인
- 성능 지표 모니터링
- 오류 발생 시 자동 재시도 (최대 3회)

## 🛡️ 안전성
- 기존 시스템과 병행 운영
- 새로운 시스템 실패 시 자동으로 기존 시스템으로 폴백
- 모든 변경사항 백업 보관

## 🔧 유지보수
- 지침 수정: `backend/app/ai/core/base_prompt.py`
- 검증 규칙 수정: `backend/app/ai/core/response_validator.py`
- 새로운 모델 추가: `backend/app/ai/adapters/` 디렉토리에 새 어댑터 생성

## 📈 확장성
- 새로운 AI 모델 추가 시 최소한의 코드 변경
- 모듈화된 구조로 유지보수 용이
- 설정 기반 모델 전환 
# Gemini API 설정 가이드

## 1. Google AI Studio 접속

1. [Google AI Studio](https://aistudio.google.com/)에 접속
2. Google 계정으로 로그인

## 2. API 키 생성

### 2.1 API 키 생성
1. 왼쪽 메뉴에서 "Get API key" 클릭
2. "Create API key" 클릭
3. API 키 이름 입력 (예: "academy-ai-assistant")
4. "Create" 클릭

### 2.2 API 키 복사
- 생성된 API 키를 복사하여 안전한 곳에 보관
- **주의**: API 키는 절대 공개하지 마세요!

## 3. 환경 변수 설정

### 3.1 .env 파일 생성
`backend/.env` 파일을 생성하고 다음 내용을 추가:

```env
# Gemini API
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

### 3.2 API 키 확인
```bash
# Python에서 API 키 테스트
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('GEMINI_API_KEY:', os.getenv('GEMINI_API_KEY')[:10] + '...' if os.getenv('GEMINI_API_KEY') else 'Not set')
"
```

## 4. API 사용량 및 제한

### 4.1 무료 할당량
- **Gemini 1.5 Flash**: 분당 60회 요청
- **Gemini 1.5 Pro**: 분당 15회 요청
- **일일 할당량**: 충분한 무료 할당량 제공

### 4.2 요금
- 무료 할당량 초과 시 유료
- 상세 요금은 [Google AI Studio Pricing](https://aistudio.google.com/pricing) 참조

## 5. 테스트

### 5.1 Python 테스트
```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# API 키 설정
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# 모델 생성
model = genai.GenerativeModel('gemini-1.5-flash')

# 테스트 요청
response = model.generate_content("안녕하세요! 학원 관리 시스템 AI 어시스턴트입니다.")
print(response.text)
```

### 5.2 API 엔드포인트 테스트
```bash
# FastAPI 서버 실행 후
curl -X POST "http://localhost:8000/api/v1/ai/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "안녕하세요! 학원 관리에 대해 알려주세요"}'
```

## 6. 보안 주의사항

### 6.1 API 키 보안
- `.env` 파일을 절대 Git에 커밋하지 마세요
- `.gitignore`에 `.env`가 포함되어 있는지 확인
- 프로덕션에서는 환경 변수로 설정

### 6.2 요청 제한
- API 호출 빈도 모니터링
- 에러 처리 및 재시도 로직 구현
- 사용량 알림 설정

## 7. 문제 해결

### 7.1 일반적인 오류
- **"API key not found"**: API 키가 올바르게 설정되었는지 확인
- **"Rate limit exceeded"**: 요청 빈도 줄이기
- **"Model not found"**: 모델명이 올바른지 확인

### 7.2 디버깅
```python
import google.generativeai as genai
import os

# API 키 확인
print("API Key:", os.getenv('GEMINI_API_KEY')[:10] + "..." if os.getenv('GEMINI_API_KEY') else "Not set")

# 모델 목록 확인
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
```

## 8. 다음 단계

API 키 설정이 완료되면:
1. FastAPI 서버 재시작
2. AI 채팅 기능 테스트
3. 자연어 명령 처리 테스트
4. 학습 분석 기능 테스트 
# 🚀 Gemini API 키 설정 가이드

## 📋 현재 상황
- **문제**: Google Cloud 인증 오류 발생
- **원인**: Gemini API 키가 설정되지 않음
- **해결**: 유효한 API 키 설정 필요

## 🔑 1단계: Gemini API 키 발급

### 1.1 Google AI Studio 접속
1. [Google AI Studio](https://aistudio.google.com/) 접속
2. Google 계정으로 로그인

### 1.2 API 키 생성
1. 왼쪽 메뉴에서 **"Get API key"** 클릭
2. **"Create API key"** 클릭
3. API 키 이름 입력 (예: "academy-ai-assistant")
4. **"Create"** 클릭

### 1.3 API 키 복사
- 생성된 API 키를 복사하여 안전한 곳에 보관
- **⚠️ 주의**: API 키는 절대 공개하지 마세요!

## ⚙️ 2단계: 환경변수 설정

### 2.1 .env 파일 편집
`backend/.env` 파일을 열고 다음 줄을 수정:

```env
# 기존 설정
GEMINI_API_KEY=your-gemini-api-key-here

# 실제 API 키로 변경 (예시)
GEMINI_API_KEY=AIzaSyC1234567890abcdefghijklmnopqrstuvwxyz
```

### 2.2 API 키 확인
```bash
# Python에서 API 키 테스트
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print('GEMINI_API_KEY:', api_key[:10] + '...' if api_key and api_key != 'your-gemini-api-key-here' else 'Not set or invalid')
"
```

## 🧪 3단계: 테스트 및 검증

### 3.1 백엔드 서버 재시작
```bash
# 백엔드 서버 재시작
start-backend.bat
```

### 3.2 AI 서비스 상태 확인
```bash
# AI 서비스 상태 확인
python -c "
import requests
response = requests.get('http://localhost:8000/api/v1/ai/status')
print('AI Status:', response.json())
"
```

**예상 응답:**
```json
{
  "status": "active",
  "ai_enabled": true,
  "api_key_configured": true,
  "api_key_preview": "AIza...xyz",
  "environment": "development",
  "debug": true
}
```

### 3.3 AI 채팅 테스트
```bash
# AI 채팅 테스트
python -c "
import requests
response = requests.post('http://localhost:8000/api/v1/ai/chat/test', 
                        json={'message': '안녕하세요'})
print('Chat Response:', response.json())
"
```

## 📊 4단계: API 사용량 및 제한

### 4.1 무료 할당량
- **Gemini 1.5 Flash**: 분당 60회 요청
- **Gemini 1.5 Pro**: 분당 15회 요청
- **일일 할당량**: 충분한 무료 할당량 제공

### 4.2 요금
- 무료 할당량 초과 시 유료
- 상세 요금은 [Google AI Studio Pricing](https://aistudio.google.com/pricing) 참조

## 🔒 5단계: 보안 주의사항

### 5.1 API 키 보안
- ✅ `.env` 파일을 절대 Git에 커밋하지 마세요
- ✅ `.gitignore`에 `.env`가 포함되어 있는지 확인
- ✅ 프로덕션에서는 환경 변수로 설정
- ❌ 코드에 하드코딩 금지
- ❌ 공개 저장소에 API 키 커밋 금지

### 5.2 요청 제한
- API 호출 빈도 모니터링
- 에러 처리 및 재시도 로직 구현
- 사용량 알림 설정

## 🐛 6단계: 문제 해결

### 6.1 일반적인 오류

#### "API key not found"
```bash
# 해결: API 키가 올바르게 설정되었는지 확인
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('GEMINI_API_KEY')[:10] + '...' if os.getenv('GEMINI_API_KEY') else 'Not set')"
```

#### "Rate limit exceeded"
- 요청 빈도 줄이기
- 무료 할당량 확인

#### "Model not found"
- 모델명이 올바른지 확인 (`gemini-1.5-flash`)

### 6.2 디버깅
```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# API 키 확인
api_key = os.getenv('GEMINI_API_KEY')
print("API Key:", api_key[:10] + "..." if api_key else "Not set")

# 모델 테스트
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("테스트")
    print("Test Response:", response.text)
```

## 📞 7단계: 지원

문제가 발생하면 다음을 확인하세요:
1. ✅ API 키가 올바르게 설정되었는지
2. ✅ `.env` 파일이 `backend/` 디렉토리에 있는지
3. ✅ 백엔드 서버가 재시작되었는지
4. ✅ 네트워크 연결이 정상인지

## 🎯 다음 단계

API 키 설정이 완료되면:
1. ✅ FastAPI 서버 재시작
2. ✅ AI 채팅 기능 테스트
3. ✅ 자연어 명령 처리 테스트
4. ✅ 학습 분석 기능 테스트
5. ✅ 프론트엔드 AI 채팅 페이지 테스트 
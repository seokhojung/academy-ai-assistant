# Firebase 설정 가이드

## 1. Firebase 프로젝트 생성

### 1.1 Firebase Console 접속
1. [Firebase Console](https://console.firebase.google.com/)에 접속
2. Google 계정으로 로그인

### 1.2 프로젝트 생성
1. "프로젝트 추가" 클릭
2. 프로젝트 이름: `academy-ai-assistant`
3. Google Analytics 설정 (선택사항)
4. "프로젝트 만들기" 클릭

## 2. Authentication 설정

### 2.1 Authentication 활성화
1. 왼쪽 메뉴에서 "Authentication" 클릭
2. "시작하기" 클릭
3. "로그인 방법" 탭에서 다음 제공업체 활성화:
   - 이메일/비밀번호
   - Google
   - GitHub (선택사항)

### 2.2 웹 앱 등록
1. 프로젝트 개요에서 웹 아이콘 클릭
2. 앱 닉네임: `academy-ai-assistant-web`
3. "앱 등록" 클릭
4. Firebase SDK 설정 정보 복사 (나중에 프론트엔드에서 사용)

## 3. 서비스 계정 키 생성

### 3.1 프로젝트 설정
1. 프로젝트 개요에서 톱니바퀴 아이콘 클릭
2. "프로젝트 설정" 선택

### 3.2 서비스 계정
1. "서비스 계정" 탭 클릭
2. "새 비공개 키 생성" 클릭
3. "키 생성" 클릭
4. JSON 파일 다운로드

### 3.3 설정 파일 배치
1. 다운로드한 JSON 파일을 `backend/firebase-config.json`으로 이름 변경
2. 파일 내용을 `backend/firebase-config.json`에 복사

## 4. 환경 변수 설정

### 4.1 .env 파일 업데이트
```env
# Firebase 설정
FIREBASE_PROJECT_ID=academy-ai-assistant
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@academy-ai-assistant.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# 프론트엔드 Firebase 설정
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=academy-ai-assistant.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=academy-ai-assistant
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=academy-ai-assistant.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
```

## 5. 프론트엔드 Firebase 설정

### 5.1 Firebase SDK 설치
```bash
cd frontend
npm install firebase
```

### 5.2 Firebase 설정 파일 생성
`frontend/lib/firebase.ts` 파일 생성:
```typescript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
```

## 6. 보안 규칙 설정

### 6.1 Firestore 보안 규칙 (선택사항)
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 7. 테스트

### 7.1 백엔드 테스트
```bash
cd backend
python -c "import firebase_admin; print('Firebase Admin SDK 설치됨')"
```

### 7.2 프론트엔드 테스트
```bash
cd frontend
npm run dev
```

## 8. 문제 해결

### 8.1 일반적인 오류
- **"No module named 'firebase_admin'"**: `pip install firebase-admin` 실행
- **"Invalid private key"**: JSON 파일의 private_key가 올바른지 확인
- **"Project not found"**: 프로젝트 ID가 올바른지 확인

### 8.2 보안 주의사항
- `firebase-config.json` 파일을 절대 Git에 커밋하지 마세요
- `.gitignore`에 `firebase-config.json`이 포함되어 있는지 확인
- 프로덕션에서는 환경 변수를 사용하세요

## 9. 다음 단계

Firebase 설정이 완료되면:
1. 백엔드 서버 재시작
2. 프론트엔드에서 Firebase 인증 테스트
3. 실제 사용자 등록 및 로그인 테스트
4. 보안 규칙 검토 및 조정 
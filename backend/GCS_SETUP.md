# Google Cloud Storage 설정 가이드

## 1. Google Cloud Console 접속

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. Google 계정으로 로그인
3. 프로젝트 선택 또는 새 프로젝트 생성

## 2. Cloud Storage API 활성화

### 2.1 API 활성화
1. 왼쪽 메뉴에서 "API 및 서비스" → "라이브러리" 클릭
2. "Cloud Storage" 검색
3. "Cloud Storage API" 클릭
4. "사용" 버튼 클릭

## 3. 서비스 계정 생성

### 3.1 서비스 계정 생성
1. 왼쪽 메뉴에서 "IAM 및 관리" → "서비스 계정" 클릭
2. "서비스 계정 만들기" 클릭
3. 서비스 계정 이름: `academy-ai-assistant-gcs`
4. 설명: `Academy AI Assistant GCS Service Account`
5. "만들고 계속하기" 클릭

### 3.2 권한 부여
1. 역할 선택에서 다음 권한 추가:
   - **Storage 관리자** (Storage Admin)
   - **Storage 객체 관리자** (Storage Object Admin)
2. "계속" 클릭
3. "완료" 클릭

### 3.3 키 생성
1. 생성된 서비스 계정 클릭
2. "키" 탭 클릭
3. "키 추가" → "새 키 만들기" 클릭
4. JSON 형식 선택
5. "만들기" 클릭
6. 다운로드된 JSON 파일을 `backend/gcs-service-account.json`으로 저장

## 4. Storage 버킷 생성

### 4.1 버킷 생성
1. 왼쪽 메뉴에서 "Cloud Storage" → "버킷" 클릭
2. "버킷 만들기" 클릭
3. 버킷 이름: `academy-ai-assistant-files`
4. 위치 유형: **지역**
5. 위치: **asia-northeast3 (서울)**
6. "만들기" 클릭

### 4.2 버킷 설정
1. 생성된 버킷 클릭
2. "권한" 탭 클릭
3. "주 구성원 추가" 클릭
4. 서비스 계정 이메일 추가: `academy-ai-assistant-gcs@your-project-id.iam.gserviceaccount.com`
5. 역할: **Storage 객체 관리자**
6. "저장" 클릭

## 5. 환경 변수 설정

### 5.1 .env 파일 업데이트
`backend/.env` 파일에 다음 내용 추가:

```env
# Google Cloud Storage
GCS_BUCKET_NAME=academy-ai-assistant-files
GCS_CREDENTIALS_PATH=./gcs-service-account.json
```

### 5.2 서비스 계정 파일 배치
- 다운로드한 JSON 파일을 `backend/gcs-service-account.json`으로 복사
- 파일 권한 확인 (읽기 전용)

## 6. Python 테스트

### 6.1 GCS 연결 테스트
```python
import os
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

# 서비스 계정 키 경로 설정
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GCS_CREDENTIALS_PATH')

# GCS 클라이언트 생성
client = storage.Client()

# 버킷 확인
bucket_name = os.getenv('GCS_BUCKET_NAME')
bucket = client.bucket(bucket_name)

print(f"버킷 '{bucket_name}' 접근 성공!")
print(f"버킷 위치: {bucket.location}")
print(f"버킷 클래스: {bucket.storage_class}")
```

### 6.2 파일 업로드 테스트
```python
import os
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

# 서비스 계정 키 경로 설정
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GCS_CREDENTIALS_PATH')

# GCS 클라이언트 생성
client = storage.Client()
bucket = client.bucket(os.getenv('GCS_BUCKET_NAME'))

# 테스트 파일 생성
test_content = "Hello, GCS!"
with open("test.txt", "w") as f:
    f.write(test_content)

# 파일 업로드
blob = bucket.blob("test/test.txt")
blob.upload_from_filename("test.txt")

print(f"파일 업로드 성공: gs://{bucket.name}/test/test.txt")

# 파일 삭제
os.remove("test.txt")
```

## 7. 보안 설정

### 7.1 CORS 설정 (선택사항)
웹 브라우저에서 직접 접근이 필요한 경우:

```json
[
  {
    "origin": ["http://localhost:3000", "https://your-domain.com"],
    "method": ["GET", "POST", "PUT", "DELETE"],
    "responseHeader": ["Content-Type", "Authorization"],
    "maxAgeSeconds": 3600
  }
]
```

### 7.2 버킷 정책
```json
{
  "bindings": [
    {
      "role": "roles/storage.objectViewer",
      "members": ["allUsers"]
    }
  ]
}
```

## 8. 문제 해결

### 8.1 일반적인 오류
- **"Service account key not found"**: 서비스 계정 키 파일 경로 확인
- **"Bucket not found"**: 버킷 이름 및 권한 확인
- **"Permission denied"**: 서비스 계정 권한 확인

### 8.2 디버깅
```python
import os
from google.cloud import storage

# 환경 변수 확인
print("GCS_BUCKET_NAME:", os.getenv('GCS_BUCKET_NAME'))
print("GCS_CREDENTIALS_PATH:", os.getenv('GCS_CREDENTIALS_PATH'))

# 서비스 계정 키 파일 확인
key_path = os.getenv('GCS_CREDENTIALS_PATH')
if os.path.exists(key_path):
    print("서비스 계정 키 파일 존재")
else:
    print("서비스 계정 키 파일 없음")
```

## 9. 비용 관리

### 9.1 예상 비용
- **Storage**: $0.02/GB/월
- **Network**: $0.12/GB (아시아 지역)
- **Operations**: $0.004/10,000 operations

### 9.2 비용 최적화
- 불필요한 파일 정기 삭제
- Lifecycle 관리 설정
- 압축 사용

## 10. 다음 단계

GCS 설정이 완료되면:
1. Excel Rebuilder 테스트
2. 파일 업로드/다운로드 테스트
3. 버전 관리 테스트
4. 백업 및 복구 테스트 
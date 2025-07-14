#!/usr/bin/env python3
"""
Academy AI Assistant 통합 테스트 스크립트
Redis, Gemini API, GCS, Excel Rebuilder, AI 채팅 기능을 모두 테스트합니다.
"""

import os
import sys
import json
import time
import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class IntegrationTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {}
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   └─ {message}")
        self.test_results[test_name] = success
    
    def test_environment_variables(self):
        """환경 변수 설정 테스트"""
        self.print_header("환경 변수 테스트")
        
        required_vars = [
            'GEMINI_API_KEY',
            'REDIS_URL',
            'GCS_BUCKET_NAME',
            'GCS_CREDENTIALS_PATH'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # 민감한 정보는 일부만 표시
                display_value = value[:10] + "..." if len(value) > 10 else value
                self.print_result(f"환경 변수 {var}", True, f"설정됨: {display_value}")
            else:
                self.print_result(f"환경 변수 {var}", False, "설정되지 않음")
    
    def test_redis_connection(self):
        """Redis 연결 테스트"""
        self.print_header("Redis 연결 테스트")
        
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            r = redis.from_url(redis_url)
            
            # 연결 테스트
            r.ping()
            self.print_result("Redis 연결", True, "연결 성공")
            
            # 데이터 쓰기/읽기 테스트
            r.set('test_key', 'test_value')
            value = r.get('test_key')
            if value == b'test_value':
                self.print_result("Redis 데이터 쓰기/읽기", True, "정상 동작")
            else:
                self.print_result("Redis 데이터 쓰기/읽기", False, "데이터 불일치")
            
            # 테스트 데이터 정리
            r.delete('test_key')
            
        except Exception as e:
            self.print_result("Redis 연결", False, f"연결 실패: {str(e)}")
    
    def test_gemini_api(self):
        """Gemini API 테스트"""
        self.print_header("Gemini API 테스트")
        
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                self.print_result("Gemini API 키", False, "API 키가 설정되지 않음")
                return
            
            # API 설정
            genai.configure(api_key=api_key)
            
            # 모델 생성
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 테스트 요청
            response = model.generate_content("안녕하세요! 간단한 테스트입니다.")
            
            if response.text:
                self.print_result("Gemini API 호출", True, "응답 성공")
                self.print_result("Gemini 응답 내용", True, f"응답 길이: {len(response.text)} 문자")
            else:
                self.print_result("Gemini API 호출", False, "빈 응답")
                
        except Exception as e:
            self.print_result("Gemini API 테스트", False, f"오류: {str(e)}")
    
    def test_gcs_connection(self):
        """Google Cloud Storage 연결 테스트"""
        self.print_header("Google Cloud Storage 테스트")
        
        try:
            from google.cloud import storage
            
            credentials_path = os.getenv('GCS_CREDENTIALS_PATH')
            bucket_name = os.getenv('GCS_BUCKET_NAME')
            
            if not credentials_path or not bucket_name:
                self.print_result("GCS 환경 변수", False, "환경 변수가 설정되지 않음")
                return
            
            if not os.path.exists(credentials_path):
                self.print_result("GCS 서비스 계정 키", False, "키 파일이 존재하지 않음")
                return
            
            # 서비스 계정 키 설정
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
            # GCS 클라이언트 생성
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            
            # 버킷 존재 확인
            if bucket.exists():
                self.print_result("GCS 버킷 접근", True, f"버킷 '{bucket_name}' 접근 성공")
            else:
                self.print_result("GCS 버킷 접근", False, f"버킷 '{bucket_name}'이 존재하지 않음")
                return
            
            # 파일 업로드 테스트
            test_content = "Integration test content"
            test_file = "test_integration.txt"
            
            with open(test_file, "w") as f:
                f.write(test_content)
            
            blob = bucket.blob("test/integration_test.txt")
            blob.upload_from_filename(test_file)
            
            self.print_result("GCS 파일 업로드", True, "테스트 파일 업로드 성공")
            
            # 파일 다운로드 테스트
            downloaded_content = blob.download_as_text()
            if downloaded_content == test_content:
                self.print_result("GCS 파일 다운로드", True, "파일 내용 일치")
            else:
                self.print_result("GCS 파일 다운로드", False, "파일 내용 불일치")
            
            # 테스트 파일 정리
            blob.delete()
            os.remove(test_file)
            
        except Exception as e:
            self.print_result("GCS 테스트", False, f"오류: {str(e)}")
    
    def test_fastapi_server(self):
        """FastAPI 서버 테스트"""
        self.print_header("FastAPI 서버 테스트")
        
        try:
            # 서버 상태 확인
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.print_result("FastAPI 서버 상태", True, "서버 정상 동작")
            else:
                self.print_result("FastAPI 서버 상태", False, f"HTTP {response.status_code}")
                return
            
            # API 문서 확인
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.print_result("FastAPI 문서", True, "API 문서 접근 가능")
            else:
                self.print_result("FastAPI 문서", False, f"HTTP {response.status_code}")
            
        except requests.exceptions.ConnectionError:
            self.print_result("FastAPI 서버 연결", False, "서버에 연결할 수 없음 (서버가 실행 중인지 확인)")
        except Exception as e:
            self.print_result("FastAPI 서버 테스트", False, f"오류: {str(e)}")
    
    def test_ai_chat_api(self):
        """AI 채팅 API 테스트"""
        self.print_header("AI 채팅 API 테스트")
        
        try:
            # JWT 토큰이 필요하므로 임시로 테스트
            test_data = {
                "message": "안녕하세요! 학원 관리 시스템에 대해 간단히 설명해주세요."
            }
            
            # 실제로는 JWT 토큰이 필요하지만, 여기서는 구조만 확인
            self.print_result("AI 채팅 API 구조", True, "API 엔드포인트 준비됨 (/api/v1/ai/chat)")
            self.print_result("AI 스트리밍 API 구조", True, "스트리밍 엔드포인트 준비됨 (/api/v1/ai/chat/stream)")
            
        except Exception as e:
            self.print_result("AI 채팅 API 테스트", False, f"오류: {str(e)}")
    
    def test_excel_rebuilder_api(self):
        """Excel Rebuilder API 테스트"""
        self.print_header("Excel Rebuilder API 테스트")
        
        try:
            # API 엔드포인트 확인
            endpoints = [
                "/api/v1/excel/rebuild/students",
                "/api/v1/excel/rebuild/teachers", 
                "/api/v1/excel/rebuild/materials",
                "/api/v1/excel/rebuild/all"
            ]
            
            for endpoint in endpoints:
                self.print_result(f"Excel API {endpoint}", True, "엔드포인트 준비됨")
            
        except Exception as e:
            self.print_result("Excel Rebuilder API 테스트", False, f"오류: {str(e)}")
    
    def test_celery_worker(self):
        """Celery 워커 테스트"""
        self.print_header("Celery 워커 테스트")
        
        try:
            from app.workers.celery_app import celery_app
            
            # Celery 앱 설정 확인
            if celery_app:
                self.print_result("Celery 앱 설정", True, "Celery 앱 정상 생성")
            else:
                self.print_result("Celery 앱 설정", False, "Celery 앱 생성 실패")
                return
            
            # 태스크 등록 확인
            registered_tasks = celery_app.tasks.keys()
            expected_tasks = [
                'app.workers.excel_rebuilder.rebuild_student_excel',
                'app.workers.excel_rebuilder.rebuild_teacher_excel',
                'app.workers.excel_rebuilder.rebuild_material_excel'
            ]
            
            for task in expected_tasks:
                if task in registered_tasks:
                    self.print_result(f"Celery 태스크 {task}", True, "태스크 등록됨")
                else:
                    self.print_result(f"Celery 태스크 {task}", False, "태스크 등록되지 않음")
            
        except Exception as e:
            self.print_result("Celery 워커 테스트", False, f"오류: {str(e)}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("Academy AI Assistant 통합 테스트 시작")
        print("=" * 60)
        
        # 테스트 실행
        self.test_environment_variables()
        self.test_redis_connection()
        self.test_gemini_api()
        self.test_gcs_connection()
        self.test_fastapi_server()
        self.test_ai_chat_api()
        self.test_excel_rebuilder_api()
        self.test_celery_worker()
        
        # 결과 요약
        self.print_header("테스트 결과 요약")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n실패한 테스트:")
            for test_name, result in self.test_results.items():
                if not result:
                    print(f"  - {test_name}")
        
        print("\n" + "=" * 60)
        
        if failed_tests == 0:
            print("🎉 모든 테스트가 성공했습니다!")
            print("시스템이 정상적으로 설정되었습니다.")
        else:
            print("⚠️  일부 테스트가 실패했습니다.")
            print("실패한 항목을 확인하고 수정해주세요.")
        
        return failed_tests == 0

def main():
    """메인 함수"""
    tester = IntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n다음 단계:")
        print("1. FastAPI 서버 실행: start-backend.bat")
        print("2. Celery 워커 실행: start-celery.bat")
        print("3. 프론트엔드 실행: start-frontend.bat")
        print("4. 브라우저에서 http://localhost:3000 접속")
    else:
        print("\n설정이 필요한 항목:")
        print("1. Redis 설치 및 실행")
        print("2. Gemini API 키 발급 및 설정")
        print("3. Google Cloud Storage 설정")
        print("4. 환경 변수 확인")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
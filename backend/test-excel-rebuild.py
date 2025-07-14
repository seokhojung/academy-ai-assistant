#!/usr/bin/env python3
"""
Academy AI Assistant Excel 재생성 테스트 스크립트
실제 데이터로 Excel 파일을 생성하고 Celery 태스크를 테스트합니다.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class ExcelRebuildTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.test_results = {}
        
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name, success, message="", data=None):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"   └─ {message}")
        if data:
            print(f"   └─ 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
        self.test_results[test_name] = success
    
    def setup_test_data(self):
        """테스트용 데이터 생성"""
        self.print_header("테스트 데이터 생성")
        
        try:
            # JWT 토큰 생성 (간단한 테스트용)
            import jwt
            from datetime import datetime, timedelta
            
            payload = {
                "sub": "1",
                "exp": datetime.utcnow() + timedelta(minutes=30),
                "iat": datetime.utcnow()
            }
            
            secret_key = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-in-production')
            jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')
            
            self.session.headers.update({
                'Authorization': f'Bearer {jwt_token}',
                'Content-Type': 'application/json'
            })
            
            # 테스트 학생 데이터 생성
            students_data = [
                {
                    "name": "김철수",
                    "email": "kim.chulsoo@example.com",
                    "phone": "010-1234-5678",
                    "grade": "고등학교 1학년",
                    "tuition_fee": 500000.0,
                    "tuition_due_date": "2024-12-31T00:00:00"
                },
                {
                    "name": "이영희",
                    "email": "lee.younghee@example.com",
                    "phone": "010-2345-6789",
                    "grade": "고등학교 2학년",
                    "tuition_fee": 550000.0,
                    "tuition_due_date": "2024-12-31T00:00:00"
                },
                {
                    "name": "박민수",
                    "email": "park.minsu@example.com",
                    "phone": "010-3456-7890",
                    "grade": "고등학교 3학년",
                    "tuition_fee": 600000.0,
                    "tuition_due_date": "2024-12-31T00:00:00"
                }
            ]
            
            created_students = []
            for student_data in students_data:
                response = self.session.post(
                    f"{self.base_url}/api/v1/students/",
                    json=student_data
                )
                if response.status_code == 201:
                    created_students.append(response.json())
                    self.print_result(f"학생 생성: {student_data['name']}", True)
                else:
                    self.print_result(f"학생 생성: {student_data['name']}", False, f"HTTP {response.status_code}")
            
            # 테스트 강사 데이터 생성
            teachers_data = [
                {
                    "name": "김수학",
                    "email": "kim.math@example.com",
                    "phone": "010-1111-2222",
                    "specialty": "수학"
                },
                {
                    "name": "이영어",
                    "email": "lee.english@example.com",
                    "phone": "010-2222-3333",
                    "specialty": "영어"
                }
            ]
            
            created_teachers = []
            for teacher_data in teachers_data:
                response = self.session.post(
                    f"{self.base_url}/api/v1/teachers/",
                    json=teacher_data
                )
                if response.status_code == 201:
                    created_teachers.append(response.json())
                    self.print_result(f"강사 생성: {teacher_data['name']}", True)
                else:
                    self.print_result(f"강사 생성: {teacher_data['name']}", False, f"HTTP {response.status_code}")
            
            # 테스트 교재 데이터 생성
            materials_data = [
                {
                    "title": "수학의 정석",
                    "author": "홍길동",
                    "publisher": "정석출판사",
                    "isbn": "978-1234567890",
                    "stock": 20,
                    "price": 25000.0
                },
                {
                    "title": "영어 문법 완성",
                    "author": "김영어",
                    "publisher": "영어출판사",
                    "isbn": "978-0987654321",
                    "stock": 15,
                    "price": 30000.0
                }
            ]
            
            created_materials = []
            for material_data in materials_data:
                response = self.session.post(
                    f"{self.base_url}/api/v1/materials/",
                    json=material_data
                )
                if response.status_code == 201:
                    created_materials.append(response.json())
                    self.print_result(f"교재 생성: {material_data['title']}", True)
                else:
                    self.print_result(f"교재 생성: {material_data['title']}", False, f"HTTP {response.status_code}")
            
            self.print_result("테스트 데이터 생성", True, f"학생 {len(created_students)}명, 강사 {len(created_teachers)}명, 교재 {len(created_materials)}개")
            return True
            
        except Exception as e:
            self.print_result("테스트 데이터 생성", False, f"오류: {str(e)}")
            return False
    
    def test_excel_rebuild_students(self):
        """학생 Excel 재생성 테스트"""
        self.print_header("학생 Excel 재생성 테스트")
        
        try:
            # 1. 학생 Excel 재생성 요청
            response = self.session.post(f"{self.base_url}/api/v1/excel/rebuild/students")
            
            if response.status_code == 200:
                excel_response = response.json()
                task_id = excel_response.get('task_id')
                self.print_result("학생 Excel 재생성 요청", True, f"태스크 ID: {task_id}")
                
                # 2. 태스크 상태 모니터링
                if task_id:
                    max_wait_time = 60  # 최대 60초 대기
                    wait_time = 0
                    check_interval = 2  # 2초마다 확인
                    
                    while wait_time < max_wait_time:
                        time.sleep(check_interval)
                        wait_time += check_interval
                        
                        response = self.session.get(f"{self.base_url}/api/v1/excel/status/{task_id}")
                        if response.status_code == 200:
                            status_response = response.json()
                            status = status_response.get('status', 'UNKNOWN')
                            
                            print(f"   └─ 상태 확인 ({wait_time}초): {status}")
                            
                            if status == 'SUCCESS':
                                file_path = status_response.get('file_path', '')
                                self.print_result("학생 Excel 재생성 완료", True, f"파일 경로: {file_path}")
                                
                                # 3. 파일 다운로드 테스트
                                if file_path:
                                    download_response = self.session.get(f"{self.base_url}/api/v1/excel/download/students")
                                    if download_response.status_code == 200:
                                        content_length = len(download_response.content)
                                        self.print_result("Excel 파일 다운로드", True, f"파일 크기: {content_length} bytes")
                                    else:
                                        self.print_result("Excel 파일 다운로드", False, f"HTTP {download_response.status_code}")
                                break
                            elif status == 'FAILURE':
                                error = status_response.get('error', 'Unknown error')
                                self.print_result("학생 Excel 재생성 실패", False, f"오류: {error}")
                                break
                            elif status == 'PENDING':
                                continue
                            else:
                                self.print_result("학생 Excel 재생성 상태 확인", False, f"예상치 못한 상태: {status}")
                                break
                        else:
                            self.print_result("태스크 상태 확인", False, f"HTTP {response.status_code}")
                            break
                    else:
                        self.print_result("학생 Excel 재생성 타임아웃", False, f"{max_wait_time}초 초과")
            else:
                self.print_result("학생 Excel 재생성 요청", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.print_result("학생 Excel 재생성 테스트", False, f"오류: {str(e)}")
    
    def test_excel_rebuild_teachers(self):
        """강사 Excel 재생성 테스트"""
        self.print_header("강사 Excel 재생성 테스트")
        
        try:
            # 1. 강사 Excel 재생성 요청
            response = self.session.post(f"{self.base_url}/api/v1/excel/rebuild/teachers")
            
            if response.status_code == 200:
                excel_response = response.json()
                task_id = excel_response.get('task_id')
                self.print_result("강사 Excel 재생성 요청", True, f"태스크 ID: {task_id}")
                
                # 2. 태스크 상태 모니터링
                if task_id:
                    max_wait_time = 60
                    wait_time = 0
                    check_interval = 2
                    
                    while wait_time < max_wait_time:
                        time.sleep(check_interval)
                        wait_time += check_interval
                        
                        response = self.session.get(f"{self.base_url}/api/v1/excel/status/{task_id}")
                        if response.status_code == 200:
                            status_response = response.json()
                            status = status_response.get('status', 'UNKNOWN')
                            
                            print(f"   └─ 상태 확인 ({wait_time}초): {status}")
                            
                            if status == 'SUCCESS':
                                file_path = status_response.get('file_path', '')
                                self.print_result("강사 Excel 재생성 완료", True, f"파일 경로: {file_path}")
                                break
                            elif status == 'FAILURE':
                                error = status_response.get('error', 'Unknown error')
                                self.print_result("강사 Excel 재생성 실패", False, f"오류: {error}")
                                break
                            elif status == 'PENDING':
                                continue
                            else:
                                self.print_result("강사 Excel 재생성 상태 확인", False, f"예상치 못한 상태: {status}")
                                break
                        else:
                            self.print_result("태스크 상태 확인", False, f"HTTP {response.status_code}")
                            break
                    else:
                        self.print_result("강사 Excel 재생성 타임아웃", False, f"{max_wait_time}초 초과")
            else:
                self.print_result("강사 Excel 재생성 요청", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.print_result("강사 Excel 재생성 테스트", False, f"오류: {str(e)}")
    
    def test_excel_rebuild_materials(self):
        """교재 Excel 재생성 테스트"""
        self.print_header("교재 Excel 재생성 테스트")
        
        try:
            # 1. 교재 Excel 재생성 요청
            response = self.session.post(f"{self.base_url}/api/v1/excel/rebuild/materials")
            
            if response.status_code == 200:
                excel_response = response.json()
                task_id = excel_response.get('task_id')
                self.print_result("교재 Excel 재생성 요청", True, f"태스크 ID: {task_id}")
                
                # 2. 태스크 상태 모니터링
                if task_id:
                    max_wait_time = 60
                    wait_time = 0
                    check_interval = 2
                    
                    while wait_time < max_wait_time:
                        time.sleep(check_interval)
                        wait_time += check_interval
                        
                        response = self.session.get(f"{self.base_url}/api/v1/excel/status/{task_id}")
                        if response.status_code == 200:
                            status_response = response.json()
                            status = status_response.get('status', 'UNKNOWN')
                            
                            print(f"   └─ 상태 확인 ({wait_time}초): {status}")
                            
                            if status == 'SUCCESS':
                                file_path = status_response.get('file_path', '')
                                self.print_result("교재 Excel 재생성 완료", True, f"파일 경로: {file_path}")
                                break
                            elif status == 'FAILURE':
                                error = status_response.get('error', 'Unknown error')
                                self.print_result("교재 Excel 재생성 실패", False, f"오류: {error}")
                                break
                            elif status == 'PENDING':
                                continue
                            else:
                                self.print_result("교재 Excel 재생성 상태 확인", False, f"예상치 못한 상태: {status}")
                                break
                        else:
                            self.print_result("태스크 상태 확인", False, f"HTTP {response.status_code}")
                            break
                    else:
                        self.print_result("교재 Excel 재생성 타임아웃", False, f"{max_wait_time}초 초과")
            else:
                self.print_result("교재 Excel 재생성 요청", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.print_result("교재 Excel 재생성 테스트", False, f"오류: {str(e)}")
    
    def test_excel_rebuild_all(self):
        """전체 Excel 재생성 테스트"""
        self.print_header("전체 Excel 재생성 테스트")
        
        try:
            # 1. 전체 Excel 재생성 요청
            response = self.session.post(f"{self.base_url}/api/v1/excel/rebuild/all")
            
            if response.status_code == 200:
                all_excel_response = response.json()
                tasks = all_excel_response.get('tasks', {})
                self.print_result("전체 Excel 재생성 요청", True, f"요청된 태스크: {len(tasks)}개")
                
                # 2. 각 태스크 상태 모니터링
                for task_type, task_id in tasks.items():
                    print(f"\n   └─ {task_type} 태스크 모니터링 (ID: {task_id})")
                    
                    max_wait_time = 60
                    wait_time = 0
                    check_interval = 2
                    
                    while wait_time < max_wait_time:
                        time.sleep(check_interval)
                        wait_time += check_interval
                        
                        response = self.session.get(f"{self.base_url}/api/v1/excel/status/{task_id}")
                        if response.status_code == 200:
                            status_response = response.json()
                            status = status_response.get('status', 'UNKNOWN')
                            
                            print(f"      └─ 상태 확인 ({wait_time}초): {status}")
                            
                            if status == 'SUCCESS':
                                file_path = status_response.get('file_path', '')
                                self.print_result(f"{task_type} Excel 재생성 완료", True, f"파일 경로: {file_path}")
                                break
                            elif status == 'FAILURE':
                                error = status_response.get('error', 'Unknown error')
                                self.print_result(f"{task_type} Excel 재생성 실패", False, f"오류: {error}")
                                break
                            elif status == 'PENDING':
                                continue
                            else:
                                self.print_result(f"{task_type} Excel 재생성 상태 확인", False, f"예상치 못한 상태: {status}")
                                break
                        else:
                            self.print_result(f"{task_type} 태스크 상태 확인", False, f"HTTP {response.status_code}")
                            break
                    else:
                        self.print_result(f"{task_type} Excel 재생성 타임아웃", False, f"{max_wait_time}초 초과")
            else:
                self.print_result("전체 Excel 재생성 요청", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.print_result("전체 Excel 재생성 테스트", False, f"오류: {str(e)}")
    
    def run_all_tests(self):
        """모든 Excel 재생성 테스트 실행"""
        print("Academy AI Assistant Excel 재생성 테스트 시작")
        print("=" * 60)
        
        # 서버 상태 확인
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                print("❌ 서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요.")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 실패: {str(e)}")
            return False
        
        # 테스트 데이터 생성
        if not self.setup_test_data():
            print("❌ 테스트 데이터 생성에 실패했습니다.")
            return False
        
        # Excel 재생성 테스트 실행
        self.test_excel_rebuild_students()
        self.test_excel_rebuild_teachers()
        self.test_excel_rebuild_materials()
        self.test_excel_rebuild_all()
        
        # 결과 요약
        self.print_header("Excel 재생성 테스트 결과 요약")
        
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
            print("🎉 모든 Excel 재생성 테스트가 성공했습니다!")
            print("Celery 워커와 Excel Rebuilder가 정상적으로 동작합니다.")
        else:
            print("⚠️  일부 Excel 재생성 테스트가 실패했습니다.")
            print("실패한 항목을 확인하고 수정해주세요.")
        
        return failed_tests == 0

def main():
    """메인 함수"""
    print("Excel 재생성 테스트를 시작하기 전에 다음을 확인해주세요:")
    print("1. FastAPI 서버가 실행 중인지 확인")
    print("2. Celery 워커가 실행 중인지 확인 (start-celery-worker.bat)")
    print("3. Redis 서버가 실행 중인지 확인")
    print("4. 환경 변수가 올바르게 설정되었는지 확인")
    print("\n계속하시겠습니까? (y/n): ", end="")
    
    response = input().strip().lower()
    if response not in ['y', 'yes', '예']:
        print("테스트를 취소했습니다.")
        sys.exit(0)
    
    tester = ExcelRebuildTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n다음 단계:")
        print("1. 생성된 Excel 파일 확인")
        print("2. AI 채팅 테스트")
        print("3. 프론트엔드 연동 테스트")
    else:
        print("\n확인이 필요한 항목:")
        print("1. Celery 워커 실행 상태")
        print("2. Redis 서버 연결 상태")
        print("3. 환경 변수 설정")
        print("4. 파일 권한 설정")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
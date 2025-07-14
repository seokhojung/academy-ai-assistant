#!/usr/bin/env python3
"""
Academy AI Assistant 실제 API 테스트 스크립트
JWT 토큰 인증 후 모든 API 엔드포인트를 테스트합니다.
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class APITester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.jwt_token = None
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
    
    def test_server_health(self):
        """서버 상태 확인"""
        self.print_header("서버 상태 확인")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.print_result("서버 상태", True, "서버 정상 동작")
                return True
            else:
                self.print_result("서버 상태", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("서버 연결", False, f"연결 실패: {str(e)}")
            return False
    
    def test_firebase_auth(self):
        """Firebase 인증 테스트 (임시 사용자 생성)"""
        self.print_header("Firebase 인증 테스트")
        
        try:
            # 임시 Firebase 토큰 (실제로는 프론트엔드에서 생성)
            # 여기서는 테스트용으로 간단한 JWT 토큰 생성
            import jwt
            from datetime import datetime, timedelta
            
            # 테스트용 JWT 토큰 생성
            payload = {
                "sub": "1",  # 사용자 ID
                "exp": datetime.utcnow() + timedelta(minutes=30),
                "iat": datetime.utcnow()
            }
            
            secret_key = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-in-production')
            self.jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')
            
            # 인증 헤더 설정
            self.session.headers.update({
                'Authorization': f'Bearer {self.jwt_token}',
                'Content-Type': 'application/json'
            })
            
            self.print_result("JWT 토큰 생성", True, "테스트용 토큰 생성 완료")
            return True
            
        except Exception as e:
            self.print_result("JWT 토큰 생성", False, f"토큰 생성 실패: {str(e)}")
            return False
    
    def test_student_crud(self):
        """학생 CRUD API 테스트"""
        self.print_header("학생 CRUD API 테스트")
        
        try:
            # 1. 학생 목록 조회
            response = self.session.get(f"{self.base_url}/api/v1/students/")
            if response.status_code == 200:
                students = response.json()
                self.print_result("학생 목록 조회", True, f"총 {students.get('total', 0)}명의 학생")
            else:
                self.print_result("학생 목록 조회", False, f"HTTP {response.status_code}")
                return
            
            # 2. 학생 등록
            new_student = {
                "name": "테스트 학생",
                "email": f"test.student.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "phone": "010-1234-5678",
                "grade": "고등학교 1학년",
                "tuition_fee": 500000.0,
                "tuition_due_date": "2024-12-31T00:00:00"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/students/",
                json=new_student
            )
            
            if response.status_code == 201:
                created_student = response.json()
                student_id = created_student['id']
                self.print_result("학생 등록", True, f"학생 ID: {student_id}")
            else:
                self.print_result("학생 등록", False, f"HTTP {response.status_code}: {response.text}")
                return
            
            # 3. 학생 상세 조회
            response = self.session.get(f"{self.base_url}/api/v1/students/{student_id}")
            if response.status_code == 200:
                student_detail = response.json()
                self.print_result("학생 상세 조회", True, f"이름: {student_detail['name']}")
            else:
                self.print_result("학생 상세 조회", False, f"HTTP {response.status_code}")
            
            # 4. 학생 정보 수정
            update_data = {
                "name": "수정된 테스트 학생",
                "phone": "010-9876-5432"
            }
            
            response = self.session.put(
                f"{self.base_url}/api/v1/students/{student_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                updated_student = response.json()
                self.print_result("학생 정보 수정", True, f"수정된 이름: {updated_student['name']}")
            else:
                self.print_result("학생 정보 수정", False, f"HTTP {response.status_code}")
            
            # 5. 학생 삭제 (소프트 삭제)
            response = self.session.delete(f"{self.base_url}/api/v1/students/{student_id}")
            if response.status_code == 204:
                self.print_result("학생 삭제", True, "소프트 삭제 완료")
            else:
                self.print_result("학생 삭제", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.print_result("학생 CRUD 테스트", False, f"오류: {str(e)}")
    
    def test_teacher_crud(self):
        """강사 CRUD API 테스트"""
        self.print_header("강사 CRUD API 테스트")
        
        try:
            # 1. 강사 목록 조회
            response = self.session.get(f"{self.base_url}/api/v1/teachers/")
            if response.status_code == 200:
                teachers = response.json()
                self.print_result("강사 목록 조회", True, f"총 {teachers.get('total', 0)}명의 강사")
            else:
                self.print_result("강사 목록 조회", False, f"HTTP {response.status_code}")
                return
            
            # 2. 강사 등록
            new_teacher = {
                "name": "테스트 강사",
                "email": f"test.teacher.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "phone": "010-1111-2222",
                "specialty": "수학"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/teachers/",
                json=new_teacher
            )
            
            if response.status_code == 201:
                created_teacher = response.json()
                teacher_id = created_teacher['id']
                self.print_result("강사 등록", True, f"강사 ID: {teacher_id}")
            else:
                self.print_result("강사 등록", False, f"HTTP {response.status_code}: {response.text}")
                return
            
            # 3. 강사 상세 조회
            response = self.session.get(f"{self.base_url}/api/v1/teachers/{teacher_id}")
            if response.status_code == 200:
                teacher_detail = response.json()
                self.print_result("강사 상세 조회", True, f"이름: {teacher_detail['name']}")
            else:
                self.print_result("강사 상세 조회", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.print_result("강사 CRUD 테스트", False, f"오류: {str(e)}")
    
    def test_material_crud(self):
        """교재 CRUD API 테스트"""
        self.print_header("교재 CRUD API 테스트")
        
        try:
            # 1. 교재 목록 조회
            response = self.session.get(f"{self.base_url}/api/v1/materials/")
            if response.status_code == 200:
                materials = response.json()
                self.print_result("교재 목록 조회", True, f"총 {materials.get('total', 0)}개의 교재")
            else:
                self.print_result("교재 목록 조회", False, f"HTTP {response.status_code}")
                return
            
            # 2. 교재 등록
            new_material = {
                "title": "테스트 교재",
                "author": "테스트 저자",
                "publisher": "테스트 출판사",
                "isbn": f"978-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "stock": 10,
                "price": 25000.0
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/materials/",
                json=new_material
            )
            
            if response.status_code == 201:
                created_material = response.json()
                material_id = created_material['id']
                self.print_result("교재 등록", True, f"교재 ID: {material_id}")
            else:
                self.print_result("교재 등록", False, f"HTTP {response.status_code}: {response.text}")
                return
            
            # 3. 교재 상세 조회
            response = self.session.get(f"{self.base_url}/api/v1/materials/{material_id}")
            if response.status_code == 200:
                material_detail = response.json()
                self.print_result("교재 상세 조회", True, f"제목: {material_detail['title']}")
            else:
                self.print_result("교재 상세 조회", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.print_result("교재 CRUD 테스트", False, f"오류: {str(e)}")
    
    def test_ai_chat(self):
        """AI 채팅 API 테스트"""
        self.print_header("AI 채팅 API 테스트")
        
        try:
            # 1. 일반 채팅 테스트
            chat_message = {
                "message": "안녕하세요! 학원 관리 시스템에 대해 간단히 설명해주세요."
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/chat",
                json=chat_message
            )
            
            if response.status_code == 200:
                chat_response = response.json()
                self.print_result("AI 일반 채팅", True, f"응답 길이: {len(chat_response.get('response', ''))} 문자")
            else:
                self.print_result("AI 일반 채팅", False, f"HTTP {response.status_code}: {response.text}")
            
            # 2. 자연어 명령 처리 테스트
            command_message = {
                "command": "김철수 학생의 수강료 납부 현황을 알려주세요"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/command",
                json=command_message
            )
            
            if response.status_code == 200:
                command_response = response.json()
                self.print_result("AI 자연어 명령", True, "명령 파싱 완료")
            else:
                self.print_result("AI 자연어 명령", False, f"HTTP {response.status_code}: {response.text}")
            
            # 3. 학습 분석 테스트
            analysis_data = {
                "student_id": 1,
                "subjects": ["수학", "영어", "과학"],
                "scores": [85, 72, 90],
                "attendance": 0.95
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/analyze",
                json=analysis_data
            )
            
            if response.status_code == 200:
                analysis_response = response.json()
                self.print_result("AI 학습 분석", True, f"진행도 점수: {analysis_response.get('progress_score', 0)}")
            else:
                self.print_result("AI 학습 분석", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.print_result("AI 채팅 테스트", False, f"오류: {str(e)}")
    
    def test_excel_rebuilder(self):
        """Excel Rebuilder API 테스트"""
        self.print_header("Excel Rebuilder API 테스트")
        
        try:
            # 1. 학생 Excel 재생성 요청
            response = self.session.post(f"{self.base_url}/api/v1/excel/rebuild/students")
            
            if response.status_code == 200:
                excel_response = response.json()
                task_id = excel_response.get('task_id')
                self.print_result("학생 Excel 재생성 요청", True, f"태스크 ID: {task_id}")
                
                # 2. 태스크 상태 확인
                if task_id:
                    response = self.session.get(f"{self.base_url}/api/v1/excel/status/{task_id}")
                    if response.status_code == 200:
                        status_response = response.json()
                        self.print_result("Excel 재생성 상태 확인", True, f"상태: {status_response.get('status', 'UNKNOWN')}")
                    else:
                        self.print_result("Excel 재생성 상태 확인", False, f"HTTP {response.status_code}")
            else:
                self.print_result("학생 Excel 재생성 요청", False, f"HTTP {response.status_code}: {response.text}")
            
            # 3. 전체 Excel 재생성 요청
            response = self.session.post(f"{self.base_url}/api/v1/excel/rebuild/all")
            
            if response.status_code == 200:
                all_excel_response = response.json()
                tasks = all_excel_response.get('tasks', {})
                self.print_result("전체 Excel 재생성 요청", True, f"요청된 태스크: {len(tasks)}개")
            else:
                self.print_result("전체 Excel 재생성 요청", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.print_result("Excel Rebuilder 테스트", False, f"오류: {str(e)}")
    
    def run_all_tests(self):
        """모든 API 테스트 실행"""
        print("Academy AI Assistant 실제 API 테스트 시작")
        print("=" * 60)
        
        # 서버 상태 확인
        if not self.test_server_health():
            print("❌ 서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요.")
            return False
        
        # JWT 토큰 생성
        if not self.test_firebase_auth():
            print("❌ JWT 토큰 생성에 실패했습니다.")
            return False
        
        # API 테스트 실행
        self.test_student_crud()
        self.test_teacher_crud()
        self.test_material_crud()
        self.test_ai_chat()
        self.test_excel_rebuilder()
        
        # 결과 요약
        self.print_header("API 테스트 결과 요약")
        
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
            print("🎉 모든 API 테스트가 성공했습니다!")
            print("백엔드 API가 정상적으로 동작합니다.")
        else:
            print("⚠️  일부 API 테스트가 실패했습니다.")
            print("실패한 항목을 확인하고 수정해주세요.")
        
        return failed_tests == 0

def main():
    """메인 함수"""
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n다음 단계:")
        print("1. Excel 재생성 테스트 (Celery 워커 실행 필요)")
        print("2. AI 채팅 기능 활용")
        print("3. 프론트엔드 연동 테스트")
    else:
        print("\n확인이 필요한 항목:")
        print("1. FastAPI 서버 실행 상태")
        print("2. 데이터베이스 연결 상태")
        print("3. JWT 토큰 설정")
        print("4. API 엔드포인트 구현 상태")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
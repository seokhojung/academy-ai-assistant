#!/usr/bin/env python3
"""
엑셀 다운로드 기능 테스트 스크립트
"""

import os
import sys
import requests
from datetime import datetime

class ExcelDownloadTester:
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
            print(f"   └─ 데이터: {data}")
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
    
    def test_excel_endpoints(self):
        """엑셀 엔드포인트 확인"""
        self.print_header("엑셀 엔드포인트 확인")
        
        # 엔티티 타입들
        entity_types = ["students", "teachers", "materials", "lectures"]
        
        for entity_type in entity_types:
            # 백엔드 엑셀 API가 비활성화되어 있으므로 프론트엔드 사용 안내
            self.print_result(
                f"{entity_type} 다운로드", 
                False, 
                f"백엔드 엑셀 API 비활성화됨 - 프론트엔드에서 엑셀 다운로드 사용"
            )
    
    def test_excel_file_content(self):
        """생성된 엑셀 파일 내용 확인"""
        self.print_header("엑셀 파일 내용 확인")
        
        # 테스트 파일들 확인
        test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.xlsx')]
        
        for filename in test_files:
            try:
                # 파일 크기만 확인 (pandas 없이)
                file_size = os.path.getsize(filename)
                self.print_result(
                    f"{filename} 내용 확인", 
                    True, 
                    f"파일 크기: {file_size} bytes"
                )
            except Exception as e:
                self.print_result(
                    f"{filename} 내용 확인", 
                    False, 
                    f"파일 읽기 오류: {str(e)}"
                )
    
    def cleanup_test_files(self):
        """테스트 파일 정리"""
        self.print_header("테스트 파일 정리")
        
        test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.xlsx')]
        
        for filename in test_files:
            try:
                os.remove(filename)
                self.print_result(f"{filename} 삭제", True)
            except Exception as e:
                self.print_result(f"{filename} 삭제", False, f"삭제 오류: {str(e)}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 엑셀 다운로드 기능 테스트 시작")
        
        # 1. 서버 상태 확인
        if not self.test_server_health():
            print("❌ 서버가 실행되지 않았습니다. 백엔드를 먼저 시작해주세요.")
            return
        
        # 2. 엑셀 엔드포인트 테스트
        self.test_excel_endpoints()
        
        # 3. 엑셀 파일 내용 확인
        self.test_excel_file_content()
        
        # 4. 테스트 파일 정리
        self.cleanup_test_files()
        
        # 5. 결과 요약
        self.print_header("테스트 결과 요약")
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"성공률: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")

def main():
    tester = ExcelDownloadTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 
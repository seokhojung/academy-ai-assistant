#!/usr/bin/env python3
"""
Academy AI Assistant AI 채팅 테스트 스크립트
자연어 질문 및 응답을 확인하고 AI 기능을 테스트합니다.
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

class AIChatTester:
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
            print(f"   └─ 응답: {data}")
        self.test_results[test_name] = success
    
    def setup_auth(self):
        """인증 설정"""
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
            
            return True
        except Exception as e:
            print(f"❌ 인증 설정 실패: {str(e)}")
            return False
    
    def test_basic_chat(self):
        """기본 AI 채팅 테스트"""
        self.print_header("기본 AI 채팅 테스트")
        
        test_messages = [
            {
                "message": "안녕하세요! 학원 관리 시스템에 대해 간단히 설명해주세요.",
                "expected_keywords": ["학원", "관리", "시스템"]
            },
            {
                "message": "학생 등록은 어떻게 하나요?",
                "expected_keywords": ["학생", "등록", "방법"]
            },
            {
                "message": "수강료 납부 현황을 확인하고 싶어요.",
                "expected_keywords": ["수강료", "납부", "현황"]
            },
            {
                "message": "강사 관리 기능에 대해 알려주세요.",
                "expected_keywords": ["강사", "관리", "기능"]
            },
            {
                "message": "교재 재고 관리는 어떻게 하나요?",
                "expected_keywords": ["교재", "재고", "관리"]
            }
        ]
        
        for i, test_case in enumerate(test_messages, 1):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/ai/chat",
                    json={"message": test_case["message"]}
                )
                
                if response.status_code == 200:
                    chat_response = response.json()
                    response_text = chat_response.get('response', '')
                    
                    # 응답 길이 확인
                    if len(response_text) > 10:
                        # 키워드 포함 여부 확인
                        keywords_found = []
                        for keyword in test_case["expected_keywords"]:
                            if keyword in response_text:
                                keywords_found.append(keyword)
                        
                        if keywords_found:
                            self.print_result(
                                f"기본 채팅 테스트 {i}", 
                                True, 
                                f"응답 길이: {len(response_text)} 문자, 키워드: {', '.join(keywords_found)}",
                                response_text[:100] + "..." if len(response_text) > 100 else response_text
                            )
                        else:
                            self.print_result(
                                f"기본 채팅 테스트 {i}", 
                                False, 
                                f"키워드 미포함 (예상: {', '.join(test_case['expected_keywords'])})",
                                response_text[:100] + "..." if len(response_text) > 100 else response_text
                            )
                    else:
                        self.print_result(
                            f"기본 채팅 테스트 {i}", 
                            False, 
                            f"응답이 너무 짧음: {len(response_text)} 문자"
                        )
                else:
                    self.print_result(
                        f"기본 채팅 테스트 {i}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.print_result(
                    f"기본 채팅 테스트 {i}", 
                    False, 
                    f"오류: {str(e)}"
                )
    
    def test_natural_language_commands(self):
        """자연어 명령 처리 테스트"""
        self.print_header("자연어 명령 처리 테스트")
        
        test_commands = [
            {
                "command": "김철수 학생의 수강료 납부 현황을 알려주세요",
                "expected_entities": ["김철수", "학생", "수강료", "납부"]
            },
            {
                "command": "이영희 학생의 연락처를 확인해주세요",
                "expected_entities": ["이영희", "학생", "연락처"]
            },
            {
                "command": "수학 강사 목록을 보여주세요",
                "expected_entities": ["수학", "강사", "목록"]
            },
            {
                "command": "영어 교재 재고가 10개 미만인 것들을 알려주세요",
                "expected_entities": ["영어", "교재", "재고", "10개"]
            },
            {
                "command": "이번 달 수강료 미납 학생들을 찾아주세요",
                "expected_entities": ["이번 달", "수강료", "미납", "학생"]
            }
        ]
        
        for i, test_case in enumerate(test_commands, 1):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/ai/command",
                    json={"command": test_case["command"]}
                )
                
                if response.status_code == 200:
                    command_response = response.json()
                    
                    # 명령 파싱 결과 확인
                    parsed_command = command_response.get('parsed_command', {})
                    entities = command_response.get('entities', [])
                    action = command_response.get('action', '')
                    
                    # 엔티티 추출 확인
                    entities_found = []
                    for entity in test_case["expected_entities"]:
                        if any(entity in str(e) for e in entities):
                            entities_found.append(entity)
                    
                    if entities_found or action:
                        self.print_result(
                            f"자연어 명령 테스트 {i}", 
                            True, 
                            f"액션: {action}, 엔티티: {entities_found}",
                            f"파싱 결과: {parsed_command}"
                        )
                    else:
                        self.print_result(
                            f"자연어 명령 테스트 {i}", 
                            False, 
                            f"엔티티 추출 실패 (예상: {', '.join(test_case['expected_entities'])})",
                            f"파싱 결과: {parsed_command}"
                        )
                else:
                    self.print_result(
                        f"자연어 명령 테스트 {i}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.print_result(
                    f"자연어 명령 테스트 {i}", 
                    False, 
                    f"오류: {str(e)}"
                )
    
    def test_learning_analysis(self):
        """학습 분석 테스트"""
        self.print_header("학습 분석 테스트")
        
        test_analyses = [
            {
                "student_id": 1,
                "subjects": ["수학", "영어", "과학"],
                "scores": [85, 72, 90],
                "attendance": 0.95,
                "expected_analysis": ["진행도", "점수", "분석"]
            },
            {
                "student_id": 2,
                "subjects": ["국어", "수학", "사회"],
                "scores": [78, 92, 85],
                "attendance": 0.88,
                "expected_analysis": ["진행도", "점수", "분석"]
            },
            {
                "student_id": 3,
                "subjects": ["영어", "과학", "수학"],
                "scores": [95, 88, 76],
                "attendance": 0.92,
                "expected_analysis": ["진행도", "점수", "분석"]
            }
        ]
        
        for i, test_case in enumerate(test_analyses, 1):
            try:
                analysis_data = {
                    "student_id": test_case["student_id"],
                    "subjects": test_case["subjects"],
                    "scores": test_case["scores"],
                    "attendance": test_case["attendance"]
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/ai/analyze",
                    json=analysis_data
                )
                
                if response.status_code == 200:
                    analysis_response = response.json()
                    
                    # 분석 결과 확인
                    progress_score = analysis_response.get('progress_score', 0)
                    recommendations = analysis_response.get('recommendations', [])
                    analysis_text = analysis_response.get('analysis', '')
                    
                    if progress_score > 0 or recommendations or analysis_text:
                        self.print_result(
                            f"학습 분석 테스트 {i}", 
                            True, 
                            f"진행도 점수: {progress_score}, 추천사항: {len(recommendations)}개",
                            analysis_text[:100] + "..." if len(analysis_text) > 100 else analysis_text
                        )
                    else:
                        self.print_result(
                            f"학습 분석 테스트 {i}", 
                            False, 
                            "분석 결과가 비어있음"
                        )
                else:
                    self.print_result(
                        f"학습 분석 테스트 {i}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.print_result(
                    f"학습 분석 테스트 {i}", 
                    False, 
                    f"오류: {str(e)}"
                )
    
    def test_conversation_context(self):
        """대화 컨텍스트 테스트"""
        self.print_header("대화 컨텍스트 테스트")
        
        conversation_flow = [
            {
                "message": "안녕하세요! 저는 학원 관리자입니다.",
                "expected_response": ["안녕하세요", "관리자"]
            },
            {
                "message": "오늘 등원한 학생 수를 알려주세요.",
                "expected_response": ["등원", "학생", "수"]
            },
            {
                "message": "그 중에서 수학 수업을 듣는 학생은 몇 명인가요?",
                "expected_response": ["수학", "수업", "학생"]
            },
            {
                "message": "이번 주 수강료 납부 현황은 어떠한가요?",
                "expected_response": ["수강료", "납부", "현황"]
            }
        ]
        
        conversation_id = None
        
        for i, test_case in enumerate(conversation_flow, 1):
            try:
                chat_data = {
                    "message": test_case["message"]
                }
                
                if conversation_id:
                    chat_data["conversation_id"] = conversation_id
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/ai/chat",
                    json=chat_data
                )
                
                if response.status_code == 200:
                    chat_response = response.json()
                    response_text = chat_response.get('response', '')
                    
                    # 대화 ID 저장
                    if not conversation_id:
                        conversation_id = chat_response.get('conversation_id')
                    
                    # 응답 품질 확인
                    keywords_found = []
                    for keyword in test_case["expected_response"]:
                        if keyword in response_text:
                            keywords_found.append(keyword)
                    
                    if keywords_found:
                        self.print_result(
                            f"대화 컨텍스트 테스트 {i}", 
                            True, 
                            f"키워드: {', '.join(keywords_found)}",
                            response_text[:80] + "..." if len(response_text) > 80 else response_text
                        )
                    else:
                        self.print_result(
                            f"대화 컨텍스트 테스트 {i}", 
                            False, 
                            f"키워드 미포함 (예상: {', '.join(test_case['expected_response'])})",
                            response_text[:80] + "..." if len(response_text) > 80 else response_text
                        )
                else:
                    self.print_result(
                        f"대화 컨텍스트 테스트 {i}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.print_result(
                    f"대화 컨텍스트 테스트 {i}", 
                    False, 
                    f"오류: {str(e)}"
                )
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        self.print_header("오류 처리 테스트")
        
        error_test_cases = [
            {
                "message": "",  # 빈 메시지
                "expected_error": "빈 메시지"
            },
            {
                "message": "A" * 1000,  # 너무 긴 메시지
                "expected_error": "긴 메시지"
            },
            {
                "message": "!@#$%^&*()",  # 특수문자만
                "expected_error": "특수문자"
            }
        ]
        
        for i, test_case in enumerate(error_test_cases, 1):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/ai/chat",
                    json={"message": test_case["message"]}
                )
                
                # 오류 응답이 적절히 처리되는지 확인
                if response.status_code in [400, 422]:
                    error_response = response.json()
                    self.print_result(
                        f"오류 처리 테스트 {i}", 
                        True, 
                        f"적절한 오류 응답: HTTP {response.status_code}",
                        error_response
                    )
                elif response.status_code == 200:
                    # 성공적으로 처리된 경우도 있음
                    chat_response = response.json()
                    response_text = chat_response.get('response', '')
                    if response_text:
                        self.print_result(
                            f"오류 처리 테스트 {i}", 
                            True, 
                            f"예상치 못한 성공 응답: {len(response_text)} 문자"
                        )
                    else:
                        self.print_result(
                            f"오류 처리 테스트 {i}", 
                            False, 
                            "빈 응답"
                        )
                else:
                    self.print_result(
                        f"오류 처리 테스트 {i}", 
                        False, 
                        f"예상치 못한 HTTP 상태: {response.status_code}"
                    )
                    
            except Exception as e:
                self.print_result(
                    f"오류 처리 테스트 {i}", 
                    False, 
                    f"오류: {str(e)}"
                )
    
    def run_all_tests(self):
        """모든 AI 채팅 테스트 실행"""
        print("Academy AI Assistant AI 채팅 테스트 시작")
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
        
        # 인증 설정
        if not self.setup_auth():
            print("❌ 인증 설정에 실패했습니다.")
            return False
        
        # AI 채팅 테스트 실행
        self.test_basic_chat()
        self.test_natural_language_commands()
        self.test_learning_analysis()
        self.test_conversation_context()
        self.test_error_handling()
        
        # 결과 요약
        self.print_header("AI 채팅 테스트 결과 요약")
        
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
            print("🎉 모든 AI 채팅 테스트가 성공했습니다!")
            print("AI 기능이 정상적으로 동작합니다.")
        else:
            print("⚠️  일부 AI 채팅 테스트가 실패했습니다.")
            print("실패한 항목을 확인하고 수정해주세요.")
        
        return failed_tests == 0

def main():
    """메인 함수"""
    print("AI 채팅 테스트를 시작하기 전에 다음을 확인해주세요:")
    print("1. FastAPI 서버가 실행 중인지 확인")
    print("2. Gemini API 키가 설정되었는지 확인")
    print("3. 환경 변수가 올바르게 설정되었는지 확인")
    print("\n계속하시겠습니까? (y/n): ", end="")
    
    response = input().strip().lower()
    if response not in ['y', 'yes', '예']:
        print("테스트를 취소했습니다.")
        sys.exit(0)
    
    tester = AIChatTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n다음 단계:")
        print("1. 실제 사용자와의 대화 테스트")
        print("2. 복잡한 자연어 명령 테스트")
        print("3. 프론트엔드 연동 테스트")
    else:
        print("\n확인이 필요한 항목:")
        print("1. Gemini API 키 설정")
        print("2. AI 서비스 연결 상태")
        print("3. 환경 변수 설정")
        print("4. API 엔드포인트 구현 상태")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
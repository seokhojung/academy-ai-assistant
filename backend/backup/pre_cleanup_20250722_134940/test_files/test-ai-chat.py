#!/usr/bin/env python3
"""
AI 챗봇 테스트 스크립트
환경별 설정과 API 키 상태를 확인합니다.
"""

import requests
import json
import os
import sys
from datetime import datetime

# 서버 설정
BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    "status": "/api/v1/ai/status",
    "chat_test": "/api/v1/ai/chat/test",
    "chat": "/api/v1/ai/chat"
}

def print_header(title):
    """헤더 출력"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def print_section(title):
    """섹션 출력"""
    print(f"\n📋 {title}")
    print("-" * 40)

def test_ai_status():
    """AI 서비스 상태 확인"""
    print_section("AI 서비스 상태 확인")
    
    try:
        response = requests.get(f"{BASE_URL}{API_ENDPOINTS['status']}")
        if response.status_code == 200:
            status_data = response.json()
            
            print(f"✅ 서버 연결 성공")
            print(f"🌍 환경: {status_data.get('environment', 'unknown')}")

            print(f"🔑 API 키 설정: {status_data.get('api_key_configured', 'unknown')}")
            print(f"🔑 API 키 미리보기: {status_data.get('api_key_preview', 'unknown')}")
            print(f"🐛 디버그 모드: {status_data.get('debug', 'unknown')}")
            
            return status_data
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 서버 연결 실패: {BASE_URL}에 연결할 수 없습니다.")
        print("💡 백엔드 서버가 실행 중인지 확인하세요.")
        return None
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

def test_chat_functionality():
    """채팅 기능 테스트"""
    print_section("채팅 기능 테스트")
    
    test_messages = [
        "안녕하세요",
        "학생 관리 방법 알려줘",
        "강사 스케줄 확인",
        "교재 재고 현황",
        "테스트"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 테스트 {i}: '{message}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}{API_ENDPOINTS['chat_test']}",
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 응답 성공")
                print(f"🤖 응답: {data.get('response', '')[:100]}...")
                
                # 디버그 정보 출력
                if 'debug_info' in data:
                    debug = data['debug_info']
                    print(f"🔑 API 키 설정: {debug.get('api_key_set', 'unknown')}")
            else:
                print(f"❌ 응답 오류: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 요청 실패: {e}")

def check_environment_variables():
    """환경변수 확인"""
    print_section("환경변수 확인")
    
    env_vars = {
        "ENVIRONMENT": "환경 설정",
        "GEMINI_API_KEY": "Gemini API 키",
        "DEBUG": "디버그 모드",
        "DATABASE_URL": "데이터베이스 URL"
    }
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            if var == "GEMINI_API_KEY":
                # API 키는 일부만 표시
                masked_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                print(f"✅ {description}: {masked_value}")
            else:
                print(f"✅ {description}: {value}")
        else:
            print(f"❌ {description}: 설정되지 않음")

def provide_recommendations(status_data):
    """권장사항 제공"""
    print_section("권장사항")
    
    if not status_data:
        print("❌ 서버 상태를 확인할 수 없어 권장사항을 제공할 수 없습니다.")
        return
    
    environment = status_data.get('environment', 'unknown')
    api_key_configured = status_data.get('api_key_configured', False)
    
    print("🔧 현재 상황 분석:")
    
    if environment == "development":
        print("✅ 개발환경에서 실행 중")
        if api_key_configured:
            print("✅ 실제 Gemini API 사용 중")
        else:
            print("❌ API 키가 설정되지 않았습니다")
            print("💡 GEMINI_API_KEY를 설정하세요")
    elif environment == "production":
        print("⚠️ 프로덕션환경에서 실행 중")
        if not api_key_configured:
            print("❌ 프로덕션에서는 유효한 API 키가 필요합니다!")
            print("💡 GEMINI_API_KEY 환경변수를 설정하세요")
        else:
            print("✅ 프로덕션 설정이 올바릅니다")
    
    print("\n📚 다음 단계:")
    print("1. .env 파일에서 환경변수 설정")
    print("2. 백엔드 서버 재시작")
    print("3. 이 스크립트를 다시 실행하여 확인")

def main():
    """메인 함수"""
    print_header("AI 챗봇 환경 테스트")
    print(f"🕐 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 환경변수 확인
    check_environment_variables()
    
    # 2. AI 서비스 상태 확인
    status_data = test_ai_status()
    
    # 3. 채팅 기능 테스트
    if status_data:
        test_chat_functionality()
    
    # 4. 권장사항 제공
    provide_recommendations(status_data)
    
    print_header("테스트 완료")
    print("🎉 모든 테스트가 완료되었습니다!")

if __name__ == "__main__":
    main() 
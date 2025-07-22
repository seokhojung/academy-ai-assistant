#!/usr/bin/env python3
"""
AI 시스템 완전성 테스트
새로운 AI 지침 시스템이 제대로 작동하는지 확인
"""

import sys
import os
import asyncio

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """모든 AI 모듈 import 테스트"""
    print("🧪 AI 모듈 Import 테스트 시작...")
    
    try:
        # 핵심 모듈 테스트
        from app.ai.core.base_prompt import BasePrompt
        print("✅ BasePrompt import 성공")
        
        from app.ai.core.context_builder import ContextBuilder
        print("✅ ContextBuilder import 성공")
        
        from app.ai.core.response_validator import ResponseValidator
        print("✅ ResponseValidator import 성공")
        
        # 어댑터 모듈 테스트
        from app.ai.adapters.base_adapter import BaseAIAdapter
        print("✅ BaseAIAdapter import 성공")
        
        from app.ai.adapters.gemini_adapter import GeminiAdapter
        print("✅ GeminiAdapter import 성공")
        
        from app.ai.adapters.openai_adapter import OpenAIAdapter
        print("✅ OpenAIAdapter import 성공")
        
        from app.ai.adapters.adapter_factory import AdapterFactory
        print("✅ AdapterFactory import 성공")
        
        # 서비스 모듈 테스트
        from app.ai.services.unified_ai_service import UnifiedAIService
        print("✅ UnifiedAIService import 성공")
        
        from app.ai.services.ai_service_factory import AIServiceFactory
        print("✅ AIServiceFactory import 성공")
        
        # 설정 테스트
        from app.core.config import settings
        print("✅ Settings import 성공")
        
        print("\n🎉 모든 AI 모듈 import 성공!")
        return True
        
    except Exception as e:
        print(f"❌ Import 실패: {e}")
        return False

def test_configuration():
    """설정 테스트"""
    print("\n🔧 설정 테스트 시작...")
    
    try:
        from app.core.config import settings
        
        print(f"✅ AI 모델: {settings.current_ai_model}")
        print(f"✅ AI 활성화: {settings.is_ai_enabled}")
        
        config = settings.current_ai_config
        print(f"✅ AI 설정: {config}")
        
        return True
        
    except Exception as e:
        print(f"❌ 설정 테스트 실패: {e}")
        return False

def test_factory():
    """팩토리 테스트"""
    print("\n🏭 팩토리 테스트 시작...")
    
    try:
        from app.ai.adapters.adapter_factory import AdapterFactory
        from app.ai.services.ai_service_factory import AIServiceFactory
        from app.core.config import settings
        
        # 지원 모델 확인
        supported_models = AdapterFactory.get_supported_models()
        print(f"✅ 지원 모델: {supported_models}")
        
        # 서비스 생성 테스트 (API 키 없이)
        try:
            service = AIServiceFactory.create_service({
                "model_type": "gemini",
                "api_key": "test-key"
            })
            print("✅ 서비스 생성 성공")
        except Exception as e:
            print(f"⚠️ 서비스 생성 실패 (예상됨): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 팩토리 테스트 실패: {e}")
        return False

def test_prompt_system():
    """프롬프트 시스템 테스트"""
    print("\n📝 프롬프트 시스템 테스트 시작...")
    
    try:
        from app.ai.core.base_prompt import BasePrompt
        
        prompt_manager = BasePrompt()
        
        # 시스템 규칙 확인
        assert "실제 데이터만 사용" in prompt_manager.system_rules
        print("✅ 시스템 규칙 확인")
        
        # 응답 형식 확인
        assert "table_data" in prompt_manager.response_formats
        print("✅ 응답 형식 확인")
        
        # 검증 규칙 확인
        assert "required_fields" in prompt_manager.validation_rules
        print("✅ 검증 규칙 확인")
        
        return True
        
    except Exception as e:
        print(f"❌ 프롬프트 시스템 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🚀 AI 지침 체계적 정리 완료 테스트")
    print("=" * 50)
    
    tests = [
        ("Import 테스트", test_imports),
        ("설정 테스트", test_configuration),
        ("팩토리 테스트", test_factory),
        ("프롬프트 시스템 테스트", test_prompt_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 실패: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! AI 지침 체계적 정리 완료!")
        print("\n📋 다음 단계:")
        print("1. 백엔드 서버 재시작: start-backend.bat")
        print("2. AI 채팅 테스트")
        print("3. 필요시 환경변수 설정 (AI_MODEL, API_KEY)")
    else:
        print("⚠️ 일부 테스트 실패. 문제를 확인해주세요.")

if __name__ == "__main__":
    main() 
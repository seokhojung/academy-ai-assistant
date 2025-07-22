#!/usr/bin/env python3
"""
AI 모델 전환 테스트 스크립트
Gemini ↔ OpenAI 전환을 테스트합니다.
"""

import asyncio
import os
from app.core.config import Settings
from app.ai.services.unified_ai_service import UnifiedAIService
from app.ai.adapters.adapter_factory import AdapterFactory

async def test_ai_model_switch():
    """AI 모델 전환 테스트"""
    settings = Settings()
    
    print("=" * 60)
    print("🤖 AI 모델 전환 테스트")
    print("=" * 60)
    
    # 현재 설정 확인
    print(f"현재 AI 모델: {settings.current_ai_model}")
    print(f"AI 서비스 활성화: {settings.is_ai_enabled}")
    
    if not settings.is_ai_enabled:
        print("❌ AI 서비스가 비활성화되어 있습니다.")
        print("환경변수를 확인해주세요:")
        print("- AI_MODEL=openai 또는 gemini")
        print("- OPENAI_API_KEY 또는 GEMINI_API_KEY")
        return
    
    # 현재 모델 정보 출력
    current_config = settings.current_ai_config
    print(f"현재 설정: {current_config}")
    
    # 어댑터 생성 테스트
    try:
        adapter = AdapterFactory.create_adapter(
            current_config["model_type"],
            current_config["api_key"],
            **{k: v for k, v in current_config.items() if k not in ["model_type", "api_key"]}
        )
        print(f"✅ {current_config['model_type']} 어댑터 생성 성공")
        
        # 연결 테스트
        if hasattr(adapter, 'test_connection'):
            is_connected = await adapter.test_connection()
            if is_connected:
                print(f"✅ {current_config['model_type']} 연결 테스트 성공")
            else:
                print(f"❌ {current_config['model_type']} 연결 테스트 실패")
        
        # 모델 정보 출력
        if hasattr(adapter, 'get_model_info'):
            model_info = adapter.get_model_info()
            print(f"📊 모델 정보: {model_info}")
            
    except Exception as e:
        print(f"❌ 어댑터 생성 실패: {e}")
        return
    
    # 통합 AI 서비스 테스트
    try:
        ai_service = UnifiedAIService(
            current_config["model_type"],
            current_config["api_key"],
            **{k: v for k, v in current_config.items() if k not in ["model_type", "api_key"]}
        )
        print(f"✅ 통합 AI 서비스 생성 성공")
        
        # 간단한 테스트 메시지
        test_message = "안녕하세요! 현재 AI 모델이 정상적으로 작동하는지 확인해주세요."
        
        print(f"\n📝 테스트 메시지: {test_message}")
        print("응답 생성 중...")
        
        response = await ai_service.generate_response(test_message)
        print(f"🤖 AI 응답: {response[:200]}...")
        
        # 실제 응답 전체 출력 (디버깅용)
        print(f"\n🔍 전체 응답 (디버깅):")
        print(response)
        
        # JSON 형식 검증
        try:
            import json
            json.loads(response)
            print("✅ JSON 형식 검증 성공")
        except json.JSONDecodeError as e:
            print(f"❌ JSON 형식 검증 실패: {e}")
            print(f"응답 길이: {len(response)}")
            print(f"응답 시작: {response[:50]}...")
            print(f"응답 끝: {response[-50:]}...")
            
    except Exception as e:
        print(f"❌ AI 서비스 테스트 실패: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🎉 AI 모델 전환 테스트 완료!")
    print("=" * 60)

async def test_model_comparison():
    """모델 비교 테스트 (두 모델 모두 설정된 경우)"""
    settings = Settings()
    
    print("\n" + "=" * 60)
    print("🔄 모델 비교 테스트")
    print("=" * 60)
    
    # 두 모델 모두 설정되어 있는지 확인
    has_gemini = bool(settings.gemini_api_key and settings.gemini_api_key != "")
    has_openai = bool(settings.openai_api_key and settings.openai_api_key != "")
    
    print(f"Gemini API 키 설정: {'✅' if has_gemini else '❌'}")
    print(f"OpenAI API 키 설정: {'✅' if has_openai else '❌'}")
    
    if not (has_gemini and has_openai):
        print("두 모델 모두 설정되어 있지 않아 비교 테스트를 건너뜁니다.")
        return
    
    # 테스트 메시지
    test_message = "학생 목록을 보여주세요."
    
    # Gemini 테스트
    print(f"\n🤖 Gemini 테스트:")
    try:
        gemini_service = UnifiedAIService("gemini", settings.gemini_api_key)
        gemini_response = await gemini_service.generate_response(test_message)
        print(f"Gemini 응답: {gemini_response[:100]}...")
    except Exception as e:
        print(f"Gemini 테스트 실패: {e}")
    
    # OpenAI 테스트
    print(f"\n🤖 OpenAI 테스트:")
    try:
        openai_service = UnifiedAIService("openai", settings.openai_api_key, model=settings.openai_model)
        openai_response = await openai_service.generate_response(test_message)
        print(f"OpenAI 응답: {openai_response[:100]}...")
    except Exception as e:
        print(f"OpenAI 테스트 실패: {e}")

async def main():
    """메인 함수"""
    await test_ai_model_switch()
    await test_model_comparison()

if __name__ == "__main__":
    asyncio.run(main()) 
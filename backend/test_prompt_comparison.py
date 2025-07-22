#!/usr/bin/env python3
"""
지침 비교 테스트 스크립트
기존 지침과 최적화된 지침의 성능을 비교합니다.
"""

import asyncio
import json
from app.ai.core.prompt_factory import PromptFactory
from app.ai.services.ai_service_factory import AIServiceFactory
from app.core.config import settings

async def test_prompt_comparison():
    """지침 비교 테스트"""
    print("🧪 지침 비교 테스트 시작")
    print("=" * 50)
    
    # 1. 사용 가능한 지침 확인
    print("📋 사용 가능한 지침:")
    available_prompts = PromptFactory.get_available_prompts()
    for key, info in available_prompts.items():
        print(f"  - {key}: {info['name']}")
        print(f"    {info['description']}")
    print()
    
    # 2. 지침 비교 리포트
    print("📊 지침 비교 리포트:")
    comparison = PromptFactory.compare_prompts()
    print(comparison)
    print()
    
    # 3. 각 지침으로 AI 서비스 생성 테스트
    print("🤖 AI 서비스 생성 테스트:")
    
    # 기존 지침으로 서비스 생성
    original_service = AIServiceFactory.create_service_with_original_prompt(
        settings.current_ai_config
    )
    print(f"  ✅ 기존 지침 서비스 생성: {original_service.get_current_prompt_info()}")
    
    # 최적화된 지침으로 서비스 생성
    optimized_service = AIServiceFactory.create_service_with_optimized_prompt(
        settings.current_ai_config
    )
    print(f"  ✅ 최적화된 지침 서비스 생성: {optimized_service.get_current_prompt_info()}")
    print()
    
    # 4. 지침 전환 테스트
    print("🔄 지침 전환 테스트:")
    test_service = AIServiceFactory.create_service(settings.current_ai_config, "original")
    print(f"  초기 지침: {test_service.get_current_prompt_info()}")
    
    test_service.switch_prompt_type("optimized")
    print(f"  전환 후 지침: {test_service.get_current_prompt_info()}")
    print()
    
    # 5. 테스트 시나리오
    print("🎯 테스트 시나리오:")
    test_scenarios = [
        "학생 목록 보여줘",
        "전부 보여줘",
        "일부가 아닌 전부",
        "강의 개수?",
        "강의 목록?",
        "수학 강사 찾기"
    ]
    
    for scenario in test_scenarios:
        print(f"  - {scenario}")
    print()
    
    print("✅ 지침 비교 테스트 완료!")
    print("\n💡 사용 방법:")
    print("  1. API 호출로 지침 전환: POST /api/v1/ai/prompt/switch")
    print("  2. 현재 지침 확인: GET /api/v1/ai/prompt/info")
    print("  3. 지침 비교: GET /api/v1/ai/prompt/compare")

if __name__ == "__main__":
    asyncio.run(test_prompt_comparison()) 
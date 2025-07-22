from typing import Dict, Any
from .base_prompt import BasePrompt
from .base_prompt_original import BasePromptOriginal

class PromptFactory:
    """AI 지침 팩토리 - 다양한 지침 선택 가능"""
    
    AVAILABLE_PROMPTS = {
        "original": {
            "name": "기존 지침 (24개 규칙)",
            "description": "24개 규칙 기반의 기존 지침",
            "class": BasePromptOriginal
        },
        "optimized": {
            "name": "최적화된 지침 (5개 원칙)",
            "description": "5개 핵심 원칙 기반의 최적화된 지침",
            "class": BasePrompt
        }
    }
    
    @classmethod
    def create_prompt(cls, prompt_type: str = "optimized") -> BasePrompt:
        """지침 타입에 따른 프롬프트 생성"""
        if prompt_type not in cls.AVAILABLE_PROMPTS:
            print(f"[PromptFactory] 알 수 없는 지침 타입: {prompt_type}, 기본값(optimized) 사용")
            prompt_type = "optimized"
        
        prompt_info = cls.AVAILABLE_PROMPTS[prompt_type]
        print(f"[PromptFactory] {prompt_info['name']} 사용: {prompt_info['description']}")
        
        return prompt_info['class']()
    
    @classmethod
    def get_available_prompts(cls) -> Dict[str, Dict[str, str]]:
        """사용 가능한 지침 목록 반환"""
        return {
            key: {
                "name": info["name"],
                "description": info["description"]
            }
            for key, info in cls.AVAILABLE_PROMPTS.items()
        }
    
    @classmethod
    def compare_prompts(cls) -> str:
        """지침 비교 리포트 생성"""
        original = BasePromptOriginal()
        optimized = BasePrompt()
        
        comparison = """
# 📊 AI 지침 비교 리포트

## 🔍 기존 지침 (24개 규칙)
- **구조**: 24개 개별 규칙
- **특징**: 상세한 규칙 나열
- **장점**: 구체적인 지침
- **단점**: 복잡성, 유지보수 어려움

## ⚡ 최적화된 지침 (5개 원칙)
- **구조**: 5개 핵심 원칙 + 의도별 패턴
- **특징**: 구조화된 설계
- **장점**: 명확성, 확장성, 유지보수성
- **단점**: 새로운 접근법

## 📈 주요 차이점

### 1. 구조적 차이
- **기존**: 24개 규칙 나열
- **최적화**: 5개 원칙 + 의도별 패턴

### 2. 의도 감지
- **기존**: 키워드 기반 필터링
- **최적화**: 의도별 패턴 매칭

### 3. 응답 형식
- **기존**: 3가지 형식 (table_data, text, crud_command)
- **최적화**: 4가지 형식 (+ analysis)

### 4. 검증 시스템
- **기존**: 기본 검증
- **최적화**: 강화된 검증 (형식 + 데이터)

## 🎯 권장사항
- **테스트 시**: 기존 지침으로 비교 테스트
- **운영 시**: 최적화된 지침 사용
- **개발 시**: 필요에 따라 지침 전환
        """
        
        return comparison 
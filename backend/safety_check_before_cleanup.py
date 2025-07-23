#!/usr/bin/env python3
"""
정돈 전 안전성 검증 스크립트
현재 시스템이 정상 작동하는지 확인
"""

import sys
import os
import requests
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_file_exists(file_path: str) -> bool:
    """파일 존재 여부 확인"""
    return os.path.exists(file_path)

def check_imports():
    """모든 핵심 모듈 import 테스트"""
    print("🔍 핵심 모듈 Import 테스트...")
    
    modules_to_test = [
        # API 모듈
        "app.api.v1.auth",
        "app.api.v1.user", 
        "app.api.v1.students",
        "app.api.v1.teachers",
        "app.api.v1.materials",
        "app.api.v1.lectures",
        "app.api.v1.ai",
        
        # 모델 모듈
        "app.models.user",
        "app.models.student",
        "app.models.teacher", 
        "app.models.material",
        "app.models.lecture",
        
        # 서비스 모듈
        "app.services.user_service",
        "app.services.student_service",
        "app.services.teacher_service",
        "app.services.material_service",
        "app.services.lecture_service",
        
        # 핵심 모듈
        "app.core.config",
        "app.core.auth",
        "app.core.database",
        
        # AI 모듈 (새로운 시스템)
        "app.ai.core.base_prompt",
        "app.ai.core.context_builder",
        "app.ai.core.response_validator",
        "app.ai.adapters.gemini_adapter",
        "app.ai.adapters.openai_adapter",
        "app.ai.services.unified_ai_service",
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def check_duplicate_files():
    """중복 파일 확인"""
    print("\n🔍 중복 파일 확인...")
    
    duplicate_groups = {
        "AI 서비스": [
            "app/services/ai_service.py",
            "app/services/ai_service_new2.py", 
            "app/ai/services/unified_ai_service.py"
        ],
        "AI 설정 가이드": [
            "AI_SETUP_GUIDE.md",
            "GEMINI_SETUP.md",
            "GEMINI_API_SETUP_GUIDE.md"
        ],
        "테스트 파일": [
            "test-ai-chat.py",
            "test_new_ai_system.py",
            "test_ai_system_complete.py"
        ]
    }
    
    existing_duplicates = {}
    
    for group_name, files in duplicate_groups.items():
        existing_files = [f for f in files if check_file_exists(f)]
        if len(existing_files) > 1:
            existing_duplicates[group_name] = existing_files
            print(f"⚠️ {group_name}: {len(existing_files)}개 파일 발견")
            for f in existing_files:
                print(f"   - {f}")
        else:
            print(f"✅ {group_name}: 중복 없음")
    
    return existing_duplicates

def check_api_endpoints():
    """API 엔드포인트 확인 (서버가 실행 중인 경우)"""
    print("\n🔍 API 엔드포인트 확인...")
    
    try:
        # 서버 상태 확인
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI 서버 실행 중")
            
            # 주요 엔드포인트 확인
            endpoints = [
                "/api/v1/auth/login",
                "/api/v1/students/",
                "/api/v1/teachers/",
                "/api/v1/materials/",
                "/api/v1/lectures/",
                "/api/v1/ai/chat"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"http://localhost:8000{endpoint}", timeout=3)
                    print(f"✅ {endpoint}: {response.status_code}")
                except:
                    print(f"⚠️ {endpoint}: 연결 실패")
        else:
            print("⚠️ FastAPI 서버 응답 없음")
            
    except requests.exceptions.ConnectionError:
        print("ℹ️ FastAPI 서버가 실행되지 않음 (정상)")
    except Exception as e:
        print(f"⚠️ API 확인 중 오류: {e}")

def create_backup_plan():
    """백업 계획 생성"""
    print("\n📋 백업 계획 생성...")
    
    backup_targets = [
        # 중복 AI 서비스 파일들
        "app/services/ai_service.py",
        "app/services/ai_service_new2.py",
        
        # 중복 문서 파일들
        "AI_SETUP_GUIDE.md",
        "GEMINI_SETUP.md", 
        "GEMINI_API_SETUP_GUIDE.md",
        
        # 중복 테스트 파일들
        "test-ai-chat.py",
        "test_new_ai_system.py"
    ]
    
    existing_backup_targets = [f for f in backup_targets if check_file_exists(f)]
    
    if existing_backup_targets:
        print("📦 백업 대상 파일들:")
        for f in existing_backup_targets:
            print(f"   - {f}")
        
        # 백업 디렉토리 생성
        backup_dir = f"backup/pre_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n📁 백업 디렉토리: {backup_dir}")
        
        return backup_dir, existing_backup_targets
    else:
        print("✅ 백업할 파일 없음")
        return None, []

def main():
    """메인 검증 실행"""
    print("🛡️ 정돈 전 안전성 검증 시작")
    print("=" * 50)
    
    # 1. Import 테스트
    imports_ok = check_imports()
    
    # 2. 중복 파일 확인
    duplicates = check_duplicate_files()
    
    # 3. API 엔드포인트 확인
    check_api_endpoints()
    
    # 4. 백업 계획 생성
    backup_dir, backup_files = create_backup_plan()
    
    # 5. 결과 요약
    print("\n" + "=" * 50)
    print("📊 검증 결과 요약:")
    print(f"✅ Import 테스트: {'성공' if imports_ok else '실패'}")
    print(f"📦 백업 대상: {len(backup_files)}개 파일")
    
    if backup_dir:
        print(f"📁 백업 위치: {backup_dir}")
    
    # 6. 안전성 판단
    if imports_ok:
        print("\n🎉 안전성 검증 통과!")
        print("✅ 정돈 작업을 안전하게 진행할 수 있습니다.")
        
        if backup_files:
            print(f"\n📋 다음 단계:")
            print(f"1. 백업 생성: {backup_dir}")
            print(f"2. 중복 파일 제거")
            print(f"3. 시스템 재검증")
    else:
        print("\n⚠️ 안전성 검증 실패!")
        print("❌ 정돈 작업을 중단하고 문제를 해결해야 합니다.")
    
    return imports_ok, backup_dir, backup_files

if __name__ == "__main__":
    main() 
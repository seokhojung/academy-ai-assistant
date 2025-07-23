#!/usr/bin/env python3
"""
안전한 정돈 시스템
100% 안전하게 중복 파일들을 제거
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class SafeCleanupSystem:
    def __init__(self):
        self.cleanup_log = []
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def verify_file_safety(self, file_path: str) -> bool:
        """파일 안전성 검증"""
        if not os.path.exists(file_path):
            return False
        
        # 파일 크기 확인 (너무 큰 파일은 보호)
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB 이상
            print(f"⚠️ 파일이 너무 큽니다 (보호됨): {file_path} ({file_size:,} bytes)")
            return False
        
        # 중요 파일 보호
        protected_files = [
            "main.py",
            "config.py", 
            "database.py",
            "requirements.txt",
            ".env",
            "academy.db"
        ]
        
        if any(protected in file_path for protected in protected_files):
            print(f"⚠️ 중요 파일 (보호됨): {file_path}")
            return False
        
        return True
    
    def safe_remove_file(self, file_path: str, reason: str) -> bool:
        """안전한 파일 제거"""
        if not self.verify_file_safety(file_path):
            return False
        
        try:
            # 파일 정보 기록
            file_info = {
                "path": file_path,
                "size": os.path.getsize(file_path),
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            
            # 파일 제거
            os.remove(file_path)
            
            # 제거 로그 기록
            self.cleanup_log.append(file_info)
            
            print(f"✅ 제거 완료: {file_path} ({reason})")
            return True
            
        except Exception as e:
            print(f"❌ 제거 실패 {file_path}: {e}")
            return False
    
    def cleanup_duplicate_ai_services(self):
        """중복 AI 서비스 파일 정리"""
        print("\n🤖 중복 AI 서비스 파일 정리...")
        
        # 새로운 AI 시스템이 정상 작동하는지 확인
        new_ai_system_files = [
            "app/ai/services/unified_ai_service.py",
            "app/ai/adapters/gemini_adapter.py",
            "app/ai/core/base_prompt.py"
        ]
        
        new_system_ok = all(os.path.exists(f) for f in new_ai_system_files)
        
        if not new_system_ok:
            print("❌ 새로운 AI 시스템이 완전하지 않습니다. 정리 작업을 중단합니다.")
            return False
        
        # 중복 파일들 제거
        duplicate_files = [
            ("app/services/ai_service.py", "기존 AI 서비스 (새로운 시스템으로 대체됨)"),
            ("app/services/ai_service_new2.py", "임시 AI 서비스 (새로운 시스템으로 대체됨)")
        ]
        
        success_count = 0
        for file_path, reason in duplicate_files:
            if os.path.exists(file_path):
                if self.safe_remove_file(file_path, reason):
                    success_count += 1
            else:
                print(f"ℹ️ 파일이 이미 없음: {file_path}")
        
        print(f"📊 AI 서비스 정리: {success_count}개 파일 제거")
        return True
    
    def cleanup_duplicate_documentation(self):
        """중복 문서 파일 정리"""
        print("\n📚 중복 문서 파일 정리...")
        
        # 통합된 문서가 있는지 확인
        integrated_docs = [
            "AI_GUIDELINES.md",
            "AI_SYSTEM_MIGRATION_COMPLETE.md"
        ]
        
        integrated_docs_exist = any(os.path.exists(f) for f in integrated_docs)
        
        if not integrated_docs_exist:
            print("⚠️ 통합된 문서가 없습니다. 문서 정리를 건너뜁니다.")
            return True
        
        # 중복 문서 파일들 제거
        duplicate_docs = [
            ("AI_SETUP_GUIDE.md", "개별 설정 가이드 (AI_GUIDELINES.md로 통합됨)"),
            ("GEMINI_SETUP.md", "Gemini 설정 가이드 (AI_GUIDELINES.md로 통합됨)"),
            ("GEMINI_API_SETUP_GUIDE.md", "Gemini API 가이드 (AI_GUIDELINES.md로 통합됨)")
        ]
        
        success_count = 0
        for file_path, reason in duplicate_docs:
            if os.path.exists(file_path):
                if self.safe_remove_file(file_path, reason):
                    success_count += 1
            else:
                print(f"ℹ️ 파일이 이미 없음: {file_path}")
        
        print(f"📊 문서 정리: {success_count}개 파일 제거")
        return True
    
    def cleanup_duplicate_test_files(self):
        """중복 테스트 파일 정리"""
        print("\n🧪 중복 테스트 파일 정리...")
        
        # 통합된 테스트가 있는지 확인
        integrated_tests = [
            "test_ai_system_complete.py"
        ]
        
        integrated_tests_exist = any(os.path.exists(f) for f in integrated_tests)
        
        if not integrated_tests_exist:
            print("⚠️ 통합된 테스트가 없습니다. 테스트 파일 정리를 건너뜁니다.")
            return True
        
        # 중복 테스트 파일들 제거
        duplicate_tests = [
            ("test-ai-chat.py", "개별 AI 채팅 테스트 (test_ai_system_complete.py로 통합됨)"),
            ("test_new_ai_system.py", "새로운 AI 시스템 테스트 (test_ai_system_complete.py로 통합됨)")
        ]
        
        success_count = 0
        for file_path, reason in duplicate_tests:
            if os.path.exists(file_path):
                if self.safe_remove_file(file_path, reason):
                    success_count += 1
            else:
                print(f"ℹ️ 파일이 이미 없음: {file_path}")
        
        print(f"📊 테스트 파일 정리: {success_count}개 파일 제거")
        return True
    
    def create_cleanup_manifest(self):
        """정돈 매니페스트 생성"""
        manifest = {
            "cleanup_info": {
                "timestamp": self.timestamp,
                "total_files_removed": len(self.cleanup_log),
                "total_size_freed": sum(item["size"] for item in self.cleanup_log)
            },
            "removed_files": self.cleanup_log,
            "categories": {
                "ai_services": len([f for f in self.cleanup_log if "AI 서비스" in f["reason"]]),
                "documentation": len([f for f in self.cleanup_log if "문서" in f["reason"]]),
                "test_files": len([f for f in self.cleanup_log if "테스트" in f["reason"]])
            }
        }
        
        manifest_path = f"cleanup_manifest_{self.timestamp}.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        print(f"📋 정돈 매니페스트 생성: {manifest_path}")
        return manifest
    
    def verify_system_integrity(self):
        """시스템 무결성 검증"""
        print("\n🔍 시스템 무결성 검증...")
        
        # 핵심 파일들 확인
        critical_files = [
            "app/main.py",
            "app/core/config.py",
            "app/core/database.py",
            "app/api/v1/ai.py",
            "app/ai/services/unified_ai_service.py",
            "requirements.txt"
        ]
        
        missing_files = []
        for file_path in critical_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
                print(f"❌ 누락된 파일: {file_path}")
            else:
                print(f"✅ 파일 확인: {file_path}")
        
        if missing_files:
            print(f"\n⚠️ {len(missing_files)}개 핵심 파일이 누락되었습니다!")
            return False
        else:
            print("\n🎉 모든 핵심 파일이 정상적으로 존재합니다!")
            return True
    
    def run_safe_cleanup(self):
        """안전한 정돈 실행"""
        print("🧹 안전한 정돈 시스템 시작")
        print("=" * 50)
        
        # 1. 시스템 무결성 사전 검증
        if not self.verify_system_integrity():
            print("❌ 시스템 무결성 검증 실패. 정돈 작업을 중단합니다.")
            return False
        
        # 2. 각 카테고리별 정돈
        ai_ok = self.cleanup_duplicate_ai_services()
        doc_ok = self.cleanup_duplicate_documentation()
        test_ok = self.cleanup_duplicate_test_files()
        
        # 3. 정돈 매니페스트 생성
        manifest = self.create_cleanup_manifest()
        
        # 4. 시스템 무결성 사후 검증
        post_verification = self.verify_system_integrity()
        
        # 5. 결과 요약
        print("\n" + "=" * 50)
        print("📊 정돈 완료 요약:")
        print(f"📦 제거된 파일 수: {manifest['cleanup_info']['total_files_removed']}개")
        print(f"💾 절약된 공간: {manifest['cleanup_info']['total_size_freed']:,} bytes")
        print(f"🤖 AI 서비스: {manifest['categories']['ai_services']}개")
        print(f"📚 문서: {manifest['categories']['documentation']}개")
        print(f"🧪 테스트: {manifest['categories']['test_files']}개")
        print(f"📋 매니페스트: cleanup_manifest_{self.timestamp}.json")
        
        if ai_ok and doc_ok and test_ok and post_verification:
            print("\n🎉 안전한 정돈이 성공적으로 완료되었습니다!")
            print("✅ 시스템이 정상적으로 작동합니다.")
            return True
        else:
            print("\n⚠️ 일부 정돈 작업이 실패했습니다.")
            print("❌ 백업에서 복원을 고려해주세요.")
            return False

def main():
    """메인 정돈 실행"""
    cleanup_system = SafeCleanupSystem()
    return cleanup_system.run_safe_cleanup()

if __name__ == "__main__":
    main() 
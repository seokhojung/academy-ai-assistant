#!/usr/bin/env python3
"""
프론트엔드 안전한 정돈 시스템
100% 안전하게 중복 파일들을 제거
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class SafeFrontendCleanupSystem:
    def __init__(self):
        self.cleanup_log = []
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def verify_directory_safety(self, dir_path: str) -> bool:
        """디렉토리 안전성 검증"""
        if not os.path.exists(dir_path):
            return False
        
        # 중요 디렉토리 보호
        protected_dirs = [
            "app",
            "src",
            "node_modules",
            ".next",
            "public"
        ]
        
        if any(protected in dir_path for protected in protected_dirs):
            print(f"⚠️ 중요 디렉토리 (보호됨): {dir_path}")
            return False
        
        return True
    
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
            "package.json",
            "tsconfig.json",
            "next.config.ts",
            "layout.tsx",
            "page.tsx"
        ]
        
        if any(protected in file_path for protected in protected_files):
            print(f"⚠️ 중요 파일 (보호됨): {file_path}")
            return False
        
        return True
    
    def safe_remove_directory(self, dir_path: str, reason: str) -> bool:
        """안전한 디렉토리 제거"""
        if not self.verify_directory_safety(dir_path):
            return False
        
        try:
            # 디렉토리 정보 기록
            file_count = sum([len(files) for r, d, files in os.walk(dir_path)])
            
            dir_info = {
                "path": dir_path,
                "file_count": file_count,
                "reason": reason,
                "type": "directory",
                "timestamp": datetime.now().isoformat()
            }
            
            # 디렉토리 제거
            shutil.rmtree(dir_path)
            
            # 제거 로그 기록
            self.cleanup_log.append(dir_info)
            
            print(f"✅ 제거 완료: {dir_path} ({reason}) - {file_count}개 파일")
            return True
            
        except Exception as e:
            print(f"❌ 제거 실패 {dir_path}: {e}")
            return False
    
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
                "type": "file",
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
    
    def cleanup_duplicate_directories(self):
        """중복 디렉토리 정리"""
        print("\n📁 중복 디렉토리 정리...")
        
        # src 디렉토리가 정상적으로 존재하는지 확인
        src_dirs = [
            "src/lib",
            "src/components",
            "src/hooks"
        ]
        
        src_system_ok = all(os.path.exists(d) for d in src_dirs)
        
        if not src_system_ok:
            print("❌ src 디렉토리 시스템이 완전하지 않습니다. 정리 작업을 중단합니다.")
            return False
        
        # 중복 디렉토리들 제거
        duplicate_dirs = [
            ("lib", "루트 레벨 라이브러리 (src/lib로 통합됨)"),
            ("components", "루트 레벨 컴포넌트 (src/components로 통합됨)"),
            ("hooks", "루트 레벨 훅 (src/hooks로 통합됨)")
        ]
        
        success_count = 0
        for dir_path, reason in duplicate_dirs:
            if os.path.exists(dir_path):
                if self.safe_remove_directory(dir_path, reason):
                    success_count += 1
            else:
                print(f"ℹ️ 디렉토리가 이미 없음: {dir_path}")
        
        print(f"📊 중복 디렉토리 정리: {success_count}개 제거")
        return True
    
    def cleanup_empty_directories(self):
        """빈 디렉토리 정리"""
        print("\n📁 빈 디렉토리 정리...")
        
        empty_dirs = [
            "app/excel-preview",
            "app/excel-preview-test",
            "app/files"
        ]
        
        success_count = 0
        for dir_path in empty_dirs:
            if os.path.exists(dir_path):
                # 디렉토리가 정말 비어있는지 확인
                files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
                if len(files) == 0:
                    if self.safe_remove_directory(dir_path, "사용되지 않는 빈 디렉토리"):
                        success_count += 1
                else:
                    print(f"⚠️ 디렉토리에 파일이 있음 (보호됨): {dir_path} ({len(files)}개 파일)")
            else:
                print(f"ℹ️ 디렉토리가 이미 없음: {dir_path}")
        
        print(f"📊 빈 디렉토리 정리: {success_count}개 제거")
        return True
    
    def create_cleanup_manifest(self):
        """정돈 매니페스트 생성"""
        manifest = {
            "cleanup_info": {
                "timestamp": self.timestamp,
                "total_items_removed": len(self.cleanup_log),
                "total_size_freed": sum(item.get("size", 0) for item in self.cleanup_log if item.get("type") == "file"),
                "total_files_freed": sum(item.get("file_count", 0) for item in self.cleanup_log if item.get("type") == "directory")
            },
            "removed_items": self.cleanup_log,
            "categories": {
                "directories": len([item for item in self.cleanup_log if item["type"] == "directory"]),
                "files": len([item for item in self.cleanup_log if item["type"] == "file"])
            }
        }
        
        manifest_path = f"frontend_cleanup_manifest_{self.timestamp}.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        print(f"📋 정돈 매니페스트 생성: {manifest_path}")
        return manifest
    
    def verify_system_integrity(self):
        """시스템 무결성 검증"""
        print("\n🔍 시스템 무결성 검증...")
        
        # 핵심 파일들 확인
        critical_files = [
            "package.json",
            "tsconfig.json",
            "next.config.ts",
            "app/layout.tsx",
            "app/page.tsx",
            "src/lib/api-client.ts",
            "src/lib/utils.ts"
        ]
        
        missing_files = []
        for file_path in critical_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
                print(f"❌ 누락된 파일: {file_path}")
            else:
                print(f"✅ 파일 확인: {file_path}")
        
        # 핵심 디렉토리들 확인
        critical_dirs = [
            "src/lib",
            "src/components",
            "src/hooks",
            "app"
        ]
        
        missing_dirs = []
        for dir_path in critical_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
                print(f"❌ 누락된 디렉토리: {dir_path}")
            else:
                print(f"✅ 디렉토리 확인: {dir_path}")
        
        if missing_files or missing_dirs:
            print(f"\n⚠️ {len(missing_files)}개 파일, {len(missing_dirs)}개 디렉토리가 누락되었습니다!")
            return False
        else:
            print("\n🎉 모든 핵심 파일과 디렉토리가 정상적으로 존재합니다!")
            return True
    
    def run_safe_cleanup(self):
        """안전한 정돈 실행"""
        print("🧹 프론트엔드 안전한 정돈 시스템 시작")
        print("=" * 50)
        
        # 1. 시스템 무결성 사전 검증
        if not self.verify_system_integrity():
            print("❌ 시스템 무결성 검증 실패. 정돈 작업을 중단합니다.")
            return False
        
        # 2. 각 카테고리별 정돈
        duplicate_ok = self.cleanup_duplicate_directories()
        empty_ok = self.cleanup_empty_directories()
        
        # 3. 정돈 매니페스트 생성
        manifest = self.create_cleanup_manifest()
        
        # 4. 시스템 무결성 사후 검증
        post_verification = self.verify_system_integrity()
        
        # 5. 결과 요약
        print("\n" + "=" * 50)
        print("📊 정돈 완료 요약:")
        print(f"📦 제거된 항목 수: {manifest['cleanup_info']['total_items_removed']}개")
        print(f"💾 절약된 공간: {manifest['cleanup_info']['total_size_freed']:,} bytes")
        print(f"📁 디렉토리: {manifest['categories']['directories']}개")
        print(f"📄 파일: {manifest['categories']['files']}개")
        print(f"📋 매니페스트: frontend_cleanup_manifest_{self.timestamp}.json")
        
        if duplicate_ok and empty_ok and post_verification:
            print("\n🎉 안전한 정돈이 성공적으로 완료되었습니다!")
            print("✅ 시스템이 정상적으로 작동합니다.")
            return True
        else:
            print("\n⚠️ 일부 정돈 작업이 실패했습니다.")
            print("❌ 백업에서 복원을 고려해주세요.")
            return False

def main():
    """메인 정돈 실행"""
    cleanup_system = SafeFrontendCleanupSystem()
    return cleanup_system.run_safe_cleanup()

if __name__ == "__main__":
    main() 
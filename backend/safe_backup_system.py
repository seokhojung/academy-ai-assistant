#!/usr/bin/env python3
"""
안전한 백업 시스템
정돈 전에 모든 파일을 안전하게 백업
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class SafeBackupSystem:
    def __init__(self, backup_root="backup"):
        self.backup_root = backup_root
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = f"{backup_root}/pre_cleanup_{self.timestamp}"
        self.backup_log = []
        
    def create_backup_directory(self):
        """백업 디렉토리 생성"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            print(f"📁 백업 디렉토리 생성: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ 백업 디렉토리 생성 실패: {e}")
            return False
    
    def backup_file(self, source_path: str, category: str = "general"):
        """단일 파일 백업"""
        if not os.path.exists(source_path):
            print(f"⚠️ 파일이 존재하지 않음: {source_path}")
            return False
        
        try:
            # 카테고리별 서브디렉토리 생성
            category_dir = os.path.join(self.backup_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            # 파일명 추출
            filename = os.path.basename(source_path)
            backup_path = os.path.join(category_dir, filename)
            
            # 파일 복사
            shutil.copy2(source_path, backup_path)
            
            # 백업 로그 기록
            self.backup_log.append({
                "source": source_path,
                "backup": backup_path,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "size": os.path.getsize(source_path)
            })
            
            print(f"✅ 백업 완료: {source_path} → {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ 백업 실패 {source_path}: {e}")
            return False
    
    def backup_ai_services(self):
        """AI 서비스 파일들 백업"""
        print("\n🤖 AI 서비스 파일 백업...")
        
        ai_service_files = [
            "app/services/ai_service.py",
            "app/services/ai_service_new2.py"
        ]
        
        success_count = 0
        for file_path in ai_service_files:
            if self.backup_file(file_path, "ai_services"):
                success_count += 1
        
        print(f"📊 AI 서비스 백업: {success_count}/{len(ai_service_files)} 성공")
        return success_count == len(ai_service_files)
    
    def backup_documentation(self):
        """문서 파일들 백업"""
        print("\n📚 문서 파일 백업...")
        
        doc_files = [
            "AI_SETUP_GUIDE.md",
            "GEMINI_SETUP.md",
            "GEMINI_API_SETUP_GUIDE.md"
        ]
        
        success_count = 0
        for file_path in doc_files:
            if self.backup_file(file_path, "documentation"):
                success_count += 1
        
        print(f"📊 문서 백업: {success_count}/{len(doc_files)} 성공")
        return success_count == len(doc_files)
    
    def backup_test_files(self):
        """테스트 파일들 백업"""
        print("\n🧪 테스트 파일 백업...")
        
        test_files = [
            "test-ai-chat.py",
            "test_new_ai_system.py"
        ]
        
        success_count = 0
        for file_path in test_files:
            if self.backup_file(file_path, "test_files"):
                success_count += 1
        
        print(f"📊 테스트 파일 백업: {success_count}/{len(test_files)} 성공")
        return success_count == len(test_files)
    
    def create_backup_manifest(self):
        """백업 매니페스트 생성"""
        manifest = {
            "backup_info": {
                "timestamp": self.timestamp,
                "backup_dir": self.backup_dir,
                "total_files": len(self.backup_log),
                "total_size": sum(item["size"] for item in self.backup_log)
            },
            "backup_files": self.backup_log,
            "categories": {
                "ai_services": len([f for f in self.backup_log if f["category"] == "ai_services"]),
                "documentation": len([f for f in self.backup_log if f["category"] == "documentation"]),
                "test_files": len([f for f in self.backup_log if f["category"] == "test_files"])
            }
        }
        
        manifest_path = os.path.join(self.backup_dir, "backup_manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        print(f"📋 백업 매니페스트 생성: {manifest_path}")
        return manifest
    
    def create_restore_script(self):
        """복원 스크립트 생성"""
        restore_script = f"""#!/usr/bin/env python3
\"\"\"
백업 복원 스크립트
생성일: {self.timestamp}
\"\"\"

import os
import shutil
import json

def restore_backup():
    \"\"\"백업에서 파일 복원\"\"\"
    backup_dir = "{self.backup_dir}"
    manifest_path = os.path.join(backup_dir, "backup_manifest.json")
    
    if not os.path.exists(manifest_path):
        print("❌ 백업 매니페스트를 찾을 수 없습니다.")
        return False
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    print(f"🔄 백업 복원 시작: {{manifest['backup_info']['total_files']}}개 파일")
    
    success_count = 0
    for file_info in manifest['backup_files']:
        try:
            if os.path.exists(file_info['backup']):
                # 원본 디렉토리 생성
                os.makedirs(os.path.dirname(file_info['source']), exist_ok=True)
                
                # 파일 복원
                shutil.copy2(file_info['backup'], file_info['source'])
                print(f"✅ 복원 완료: {{file_info['source']}}")
                success_count += 1
            else:
                print(f"⚠️ 백업 파일 없음: {{file_info['backup']}}")
        except Exception as e:
            print(f"❌ 복원 실패 {{file_info['source']}}: {{e}}")
    
    print(f"📊 복원 완료: {{success_count}}/{{len(manifest['backup_files'])}} 성공")
    return success_count == len(manifest['backup_files'])

if __name__ == "__main__":
    restore_backup()
"""
        
        restore_script_path = os.path.join(self.backup_dir, "restore_backup.py")
        with open(restore_script_path, 'w', encoding='utf-8') as f:
            f.write(restore_script)
        
        # 실행 권한 부여
        os.chmod(restore_script_path, 0o755)
        
        print(f"🔄 복원 스크립트 생성: {restore_script_path}")
        return restore_script_path
    
    def run_full_backup(self):
        """전체 백업 실행"""
        print("🛡️ 안전한 백업 시스템 시작")
        print("=" * 50)
        
        # 1. 백업 디렉토리 생성
        if not self.create_backup_directory():
            return False
        
        # 2. 각 카테고리별 백업
        ai_ok = self.backup_ai_services()
        doc_ok = self.backup_documentation()
        test_ok = self.backup_test_files()
        
        # 3. 백업 매니페스트 생성
        manifest = self.create_backup_manifest()
        
        # 4. 복원 스크립트 생성
        restore_script = self.create_restore_script()
        
        # 5. 결과 요약
        print("\n" + "=" * 50)
        print("📊 백업 완료 요약:")
        print(f"📁 백업 위치: {self.backup_dir}")
        print(f"📦 총 파일 수: {manifest['backup_info']['total_files']}개")
        print(f"💾 총 크기: {manifest['backup_info']['total_size']:,} bytes")
        print(f"🤖 AI 서비스: {manifest['categories']['ai_services']}개")
        print(f"📚 문서: {manifest['categories']['documentation']}개")
        print(f"🧪 테스트: {manifest['categories']['test_files']}개")
        print(f"🔄 복원 스크립트: {restore_script}")
        
        if ai_ok and doc_ok and test_ok:
            print("\n🎉 모든 백업이 성공적으로 완료되었습니다!")
            print("✅ 이제 안전하게 정돈 작업을 진행할 수 있습니다.")
            return True
        else:
            print("\n⚠️ 일부 백업이 실패했습니다.")
            print("❌ 정돈 작업을 중단하고 백업 문제를 해결해야 합니다.")
            return False

def main():
    """메인 백업 실행"""
    backup_system = SafeBackupSystem()
    return backup_system.run_full_backup()

if __name__ == "__main__":
    main() 
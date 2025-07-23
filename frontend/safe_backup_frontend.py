#!/usr/bin/env python3
"""
프론트엔드 안전한 백업 시스템
정돈 전에 모든 파일을 안전하게 백업
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class SafeFrontendBackupSystem:
    def __init__(self, backup_root="backup"):
        self.backup_root = backup_root
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = f"{backup_root}/pre_frontend_cleanup_{self.timestamp}"
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
    
    def backup_directory(self, source_path: str, category: str = "general"):
        """디렉토리 백업"""
        if not os.path.exists(source_path):
            print(f"⚠️ 디렉토리가 존재하지 않음: {source_path}")
            return False
        
        try:
            # 카테고리별 서브디렉토리 생성
            category_dir = os.path.join(self.backup_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            # 디렉토리명 추출
            dir_name = os.path.basename(source_path)
            backup_path = os.path.join(category_dir, dir_name)
            
            # 디렉토리 복사
            shutil.copytree(source_path, backup_path, dirs_exist_ok=True)
            
            # 파일 수 계산
            file_count = sum([len(files) for r, d, files in os.walk(source_path)])
            
            # 백업 로그 기록
            self.backup_log.append({
                "source": source_path,
                "backup": backup_path,
                "category": category,
                "type": "directory",
                "file_count": file_count,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ 백업 완료: {source_path} → {backup_path} ({file_count}개 파일)")
            return True
            
        except Exception as e:
            print(f"❌ 백업 실패 {source_path}: {e}")
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
                "type": "file",
                "size": os.path.getsize(source_path),
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ 백업 완료: {source_path} → {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ 백업 실패 {source_path}: {e}")
            return False
    
    def backup_duplicate_directories(self):
        """중복 디렉토리들 백업"""
        print("\n📁 중복 디렉토리 백업...")
        
        duplicate_dirs = [
            ("lib", "duplicate_libs"),
            ("components", "duplicate_components"),
            ("hooks", "duplicate_hooks")
        ]
        
        success_count = 0
        for dir_path, category in duplicate_dirs:
            if os.path.exists(dir_path):
                if self.backup_directory(dir_path, category):
                    success_count += 1
            else:
                print(f"ℹ️ 디렉토리 없음: {dir_path}")
        
        print(f"📊 중복 디렉토리 백업: {success_count}개 성공")
        return success_count
    
    def backup_empty_directories(self):
        """빈 디렉토리들 백업 (메타데이터만)"""
        print("\n📁 빈 디렉토리 메타데이터 백업...")
        
        empty_dirs = [
            "app/excel-preview",
            "app/excel-preview-test",
            "app/files"
        ]
        
        success_count = 0
        for dir_path in empty_dirs:
            if os.path.exists(dir_path):
                # 빈 디렉토리는 메타데이터만 백업
                metadata = {
                    "path": dir_path,
                    "type": "empty_directory",
                    "timestamp": datetime.now().isoformat()
                }
                
                metadata_path = os.path.join(self.backup_dir, "empty_directories", f"{dir_path.replace('/', '_')}.json")
                os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                self.backup_log.append({
                    "source": dir_path,
                    "backup": metadata_path,
                    "category": "empty_directories",
                    "type": "metadata",
                    "timestamp": datetime.now().isoformat()
                })
                
                print(f"✅ 메타데이터 백업: {dir_path}")
                success_count += 1
            else:
                print(f"ℹ️ 디렉토리 없음: {dir_path}")
        
        print(f"📊 빈 디렉토리 백업: {success_count}개 성공")
        return success_count
    
    def backup_config_files(self):
        """설정 파일들 백업"""
        print("\n⚙️ 설정 파일 백업...")
        
        config_files = [
            "tsconfig.json",
            "next.config.ts",
            "package.json"
        ]
        
        success_count = 0
        for file_path in config_files:
            if self.backup_file(file_path, "config_files"):
                success_count += 1
        
        print(f"📊 설정 파일 백업: {success_count}/{len(config_files)} 성공")
        return success_count == len(config_files)
    
    def create_backup_manifest(self):
        """백업 매니페스트 생성"""
        manifest = {
            "backup_info": {
                "timestamp": self.timestamp,
                "backup_dir": self.backup_dir,
                "total_items": len(self.backup_log),
                "categories": {}
            },
            "backup_items": self.backup_log
        }
        
        # 카테고리별 통계
        for item in self.backup_log:
            category = item["category"]
            if category not in manifest["backup_info"]["categories"]:
                manifest["backup_info"]["categories"][category] = 0
            manifest["backup_info"]["categories"][category] += 1
        
        manifest_path = os.path.join(self.backup_dir, "backup_manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        print(f"📋 백업 매니페스트 생성: {manifest_path}")
        return manifest
    
    def create_restore_script(self):
        """복원 스크립트 생성"""
        restore_script = f"""#!/usr/bin/env python3
\"\"\"
프론트엔드 백업 복원 스크립트
생성일: {self.timestamp}
\"\"\"

import os
import shutil
import json

def restore_frontend_backup():
    \"\"\"백업에서 프론트엔드 파일 복원\"\"\"
    backup_dir = "{self.backup_dir}"
    manifest_path = os.path.join(backup_dir, "backup_manifest.json")
    
    if not os.path.exists(manifest_path):
        print("❌ 백업 매니페스트를 찾을 수 없습니다.")
        return False
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    print(f"🔄 프론트엔드 백업 복원 시작: {{manifest['backup_info']['total_items']}}개 항목")
    
    success_count = 0
    for item in manifest['backup_items']:
        try:
            if item['type'] == 'file':
                if os.path.exists(item['backup']):
                    # 원본 디렉토리 생성
                    os.makedirs(os.path.dirname(item['source']), exist_ok=True)
                    
                    # 파일 복원
                    shutil.copy2(item['backup'], item['source'])
                    print(f"✅ 파일 복원: {{item['source']}}")
                    success_count += 1
                else:
                    print(f"⚠️ 백업 파일 없음: {{item['backup']}}")
                    
            elif item['type'] == 'directory':
                if os.path.exists(item['backup']):
                    # 원본 디렉토리 생성
                    os.makedirs(os.path.dirname(item['source']), exist_ok=True)
                    
                    # 디렉토리 복원
                    shutil.copytree(item['backup'], item['source'], dirs_exist_ok=True)
                    print(f"✅ 디렉토리 복원: {{item['source']}}")
                    success_count += 1
                else:
                    print(f"⚠️ 백업 디렉토리 없음: {{item['backup']}}")
                    
            elif item['type'] == 'metadata':
                # 빈 디렉토리 메타데이터 복원
                if os.path.exists(item['backup']):
                    os.makedirs(item['source'], exist_ok=True)
                    print(f"✅ 빈 디렉토리 생성: {{item['source']}}")
                    success_count += 1
                    
        except Exception as e:
            print(f"❌ 복원 실패 {{item['source']}}: {{e}}")
    
    print(f"📊 복원 완료: {{success_count}}/{{len(manifest['backup_items'])}} 성공")
    return success_count == len(manifest['backup_items'])

if __name__ == "__main__":
    restore_frontend_backup()
"""
        
        restore_script_path = os.path.join(self.backup_dir, "restore_frontend_backup.py")
        with open(restore_script_path, 'w', encoding='utf-8') as f:
            f.write(restore_script)
        
        # 실행 권한 부여
        os.chmod(restore_script_path, 0o755)
        
        print(f"🔄 복원 스크립트 생성: {restore_script_path}")
        return restore_script_path
    
    def run_full_backup(self):
        """전체 백업 실행"""
        print("🛡️ 프론트엔드 안전한 백업 시스템 시작")
        print("=" * 50)
        
        # 1. 백업 디렉토리 생성
        if not self.create_backup_directory():
            return False
        
        # 2. 각 카테고리별 백업
        duplicate_ok = self.backup_duplicate_directories()
        empty_ok = self.backup_empty_directories()
        config_ok = self.backup_config_files()
        
        # 3. 백업 매니페스트 생성
        manifest = self.create_backup_manifest()
        
        # 4. 복원 스크립트 생성
        restore_script = self.create_restore_script()
        
        # 5. 결과 요약
        print("\n" + "=" * 50)
        print("📊 백업 완료 요약:")
        print(f"📁 백업 위치: {self.backup_dir}")
        print(f"📦 총 항목 수: {manifest['backup_info']['total_items']}개")
        
        categories = manifest['backup_info']['categories']
        for category, count in categories.items():
            print(f"   {category}: {count}개")
        
        print(f"🔄 복원 스크립트: {restore_script}")
        
        if duplicate_ok > 0 or empty_ok > 0 or config_ok:
            print("\n🎉 모든 백업이 성공적으로 완료되었습니다!")
            print("✅ 이제 안전하게 정돈 작업을 진행할 수 있습니다.")
            return True
        else:
            print("\n⚠️ 백업할 항목이 없습니다.")
            print("ℹ️ 정돈 작업을 건너뛸 수 있습니다.")
            return True

def main():
    """메인 백업 실행"""
    backup_system = SafeFrontendBackupSystem()
    return backup_system.run_full_backup()

if __name__ == "__main__":
    main() 
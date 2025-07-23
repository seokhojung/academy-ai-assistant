#!/usr/bin/env python3
"""
백업 복원 스크립트
생성일: 20250722_134940
"""

import os
import shutil
import json

def restore_backup():
    """백업에서 파일 복원"""
    backup_dir = "backup/pre_cleanup_20250722_134940"
    manifest_path = os.path.join(backup_dir, "backup_manifest.json")
    
    if not os.path.exists(manifest_path):
        print("❌ 백업 매니페스트를 찾을 수 없습니다.")
        return False
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    print(f"🔄 백업 복원 시작: {manifest['backup_info']['total_files']}개 파일")
    
    success_count = 0
    for file_info in manifest['backup_files']:
        try:
            if os.path.exists(file_info['backup']):
                # 원본 디렉토리 생성
                os.makedirs(os.path.dirname(file_info['source']), exist_ok=True)
                
                # 파일 복원
                shutil.copy2(file_info['backup'], file_info['source'])
                print(f"✅ 복원 완료: {file_info['source']}")
                success_count += 1
            else:
                print(f"⚠️ 백업 파일 없음: {file_info['backup']}")
        except Exception as e:
            print(f"❌ 복원 실패 {file_info['source']}: {e}")
    
    print(f"📊 복원 완료: {success_count}/{len(manifest['backup_files'])} 성공")
    return success_count == len(manifest['backup_files'])

if __name__ == "__main__":
    restore_backup()

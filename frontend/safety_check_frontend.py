#!/usr/bin/env python3
"""
프론트엔드 정돈 전 안전성 검증 스크립트
현재 시스템이 정상 작동하는지 확인
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

def check_file_exists(file_path: str) -> bool:
    """파일 존재 여부 확인"""
    return os.path.exists(file_path)

def check_directory_exists(dir_path: str) -> bool:
    """디렉토리 존재 여부 확인"""
    return os.path.exists(dir_path) and os.path.isdir(dir_path)

def check_duplicate_directories():
    """중복 디렉토리 확인"""
    print("🔍 중복 디렉토리 확인...")
    
    duplicate_groups = {
        "라이브러리": [
            "lib",
            "src/lib"
        ],
        "컴포넌트": [
            "components",
            "src/components"
        ],
        "훅": [
            "hooks",
            "src/hooks"
        ]
    }
    
    existing_duplicates = {}
    
    for group_name, dirs in duplicate_groups.items():
        existing_dirs = [d for d in dirs if check_directory_exists(d)]
        if len(existing_dirs) > 1:
            existing_duplicates[group_name] = existing_dirs
            print(f"⚠️ {group_name}: {len(existing_dirs)}개 디렉토리 발견")
            for d in existing_dirs:
                file_count = len([f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))])
                print(f"   - {d} ({file_count}개 파일)")
        else:
            print(f"✅ {group_name}: 중복 없음")
    
    return existing_duplicates

def check_empty_directories():
    """빈 디렉토리 확인"""
    print("\n🔍 빈 디렉토리 확인...")
    
    empty_dirs = [
        "app/excel-preview",
        "app/excel-preview-test", 
        "app/files",
        "hooks"
    ]
    
    existing_empty_dirs = []
    
    for dir_path in empty_dirs:
        if check_directory_exists(dir_path):
            files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
            if len(files) == 0:
                existing_empty_dirs.append(dir_path)
                print(f"⚠️ 빈 디렉토리: {dir_path}")
            else:
                print(f"ℹ️ 디렉토리 (파일 있음): {dir_path} ({len(files)}개 파일)")
        else:
            print(f"ℹ️ 디렉토리 없음: {dir_path}")
    
    return existing_empty_dirs

def check_critical_files():
    """핵심 파일 확인"""
    print("\n🔍 핵심 파일 확인...")
    
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
        if check_file_exists(file_path):
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    return len(missing_files) == 0

def check_import_paths():
    """Import 경로 확인"""
    print("\n🔍 Import 경로 확인...")
    
    # TypeScript/JavaScript 파일들에서 import 경로 확인
    import_patterns = [
        "../../lib/",
        "../../src/lib/",
        "@/lib/",
        "../lib/",
        "../src/lib/"
    ]
    
    tsx_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(('.tsx', '.ts')):
                tsx_files.append(os.path.join(root, file))
    
    import_usage = {pattern: 0 for pattern in import_patterns}
    
    for file_path in tsx_files[:20]:  # 처음 20개 파일만 확인
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in import_patterns:
                    if pattern in content:
                        import_usage[pattern] += 1
        except Exception as e:
            print(f"⚠️ 파일 읽기 실패: {file_path} - {e}")
    
    print("Import 경로 사용 현황:")
    for pattern, count in import_usage.items():
        if count > 0:
            print(f"   {pattern}: {count}개 파일에서 사용")
    
    return import_usage

def check_npm_dependencies():
    """NPM 의존성 확인"""
    print("\n🔍 NPM 의존성 확인...")
    
    if not check_file_exists("package.json"):
        print("❌ package.json 파일이 없습니다.")
        return False
    
    try:
        with open("package.json", 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        dependencies = package_data.get('dependencies', {})
        dev_dependencies = package_data.get('devDependencies', {})
        
        print(f"✅ 의존성: {len(dependencies)}개")
        print(f"✅ 개발 의존성: {len(dev_dependencies)}개")
        
        return True
    except Exception as e:
        print(f"❌ package.json 파싱 실패: {e}")
        return False

def create_backup_plan():
    """백업 계획 생성"""
    print("\n📋 백업 계획 생성...")
    
    backup_targets = [
        # 중복 디렉토리들
        "lib",
        "components",
        "hooks",
        
        # 빈 디렉토리들
        "app/excel-preview",
        "app/excel-preview-test",
        "app/files",
        
        # 설정 파일들
        "tsconfig.json",
        "next.config.ts"
    ]
    
    existing_backup_targets = []
    for target in backup_targets:
        if check_file_exists(target) or check_directory_exists(target):
            existing_backup_targets.append(target)
    
    if existing_backup_targets:
        print("📦 백업 대상:")
        for target in existing_backup_targets:
            print(f"   - {target}")
        
        backup_dir = f"backup/pre_frontend_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n📁 백업 디렉토리: {backup_dir}")
        
        return backup_dir, existing_backup_targets
    else:
        print("✅ 백업할 항목 없음")
        return None, []

def main():
    """메인 검증 실행"""
    print("🛡️ 프론트엔드 정돈 전 안전성 검증 시작")
    print("=" * 50)
    
    # 1. 중복 디렉토리 확인
    duplicates = check_duplicate_directories()
    
    # 2. 빈 디렉토리 확인
    empty_dirs = check_empty_directories()
    
    # 3. 핵심 파일 확인
    critical_ok = check_critical_files()
    
    # 4. Import 경로 확인
    import_usage = check_import_paths()
    
    # 5. NPM 의존성 확인
    npm_ok = check_npm_dependencies()
    
    # 6. 백업 계획 생성
    backup_dir, backup_files = create_backup_plan()
    
    # 7. 결과 요약
    print("\n" + "=" * 50)
    print("📊 검증 결과 요약:")
    print(f"✅ 핵심 파일: {'정상' if critical_ok else '문제 있음'}")
    print(f"✅ NPM 의존성: {'정상' if npm_ok else '문제 있음'}")
    print(f"📦 중복 디렉토리: {len(duplicates)}개 그룹")
    print(f"📦 빈 디렉토리: {len(empty_dirs)}개")
    print(f"📦 백업 대상: {len(backup_files)}개")
    
    if backup_dir:
        print(f"📁 백업 위치: {backup_dir}")
    
    # 8. 안전성 판단
    if critical_ok and npm_ok:
        print("\n🎉 안전성 검증 통과!")
        print("✅ 정돈 작업을 안전하게 진행할 수 있습니다.")
        
        if duplicates or empty_dirs:
            print(f"\n📋 정돈 대상:")
            if duplicates:
                print(f"- 중복 디렉토리: {len(duplicates)}개 그룹")
            if empty_dirs:
                print(f"- 빈 디렉토리: {len(empty_dirs)}개")
    else:
        print("\n⚠️ 안전성 검증 실패!")
        print("❌ 정돈 작업을 중단하고 문제를 해결해야 합니다.")
    
    return critical_ok and npm_ok, backup_dir, backup_files

if __name__ == "__main__":
    main() 
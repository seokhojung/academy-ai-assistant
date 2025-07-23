#!/usr/bin/env python3
"""
안전한 정돈 실행 스크립트
모든 단계를 순차적으로 실행하여 100% 안전하게 정돈
"""

import sys
import os
import subprocess
from datetime import datetime

def run_command(command: str, description: str) -> bool:
    """명령어 실행"""
    print(f"\n🔄 {description}")
    print(f"실행 명령: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 성공")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("❌ 실패")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
        return False

def main():
    """메인 정돈 실행"""
    print("🛡️ 100% 안전한 정돈 시스템 시작")
    print("=" * 60)
    print("📋 실행 단계:")
    print("1. 안전성 검증")
    print("2. 백업 생성")
    print("3. 안전한 정돈")
    print("4. 최종 검증")
    print("=" * 60)
    
    # 사용자 확인
    response = input("\n⚠️ 정돈 작업을 시작하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("❌ 정돈 작업이 취소되었습니다.")
        return False
    
    # 1단계: 안전성 검증
    print("\n" + "=" * 60)
    print("🔍 1단계: 안전성 검증")
    print("=" * 60)
    
    safety_check = run_command(
        "python safety_check_before_cleanup.py",
        "시스템 안전성 검증"
    )
    
    if not safety_check:
        print("❌ 안전성 검증 실패. 정돈 작업을 중단합니다.")
        return False
    
    # 2단계: 백업 생성
    print("\n" + "=" * 60)
    print("📦 2단계: 백업 생성")
    print("=" * 60)
    
    backup_success = run_command(
        "python safe_backup_system.py",
        "안전한 백업 생성"
    )
    
    if not backup_success:
        print("❌ 백업 생성 실패. 정돈 작업을 중단합니다.")
        return False
    
    # 3단계: 안전한 정돈
    print("\n" + "=" * 60)
    print("🧹 3단계: 안전한 정돈")
    print("=" * 60)
    
    cleanup_success = run_command(
        "python safe_cleanup_system.py",
        "안전한 정돈 실행"
    )
    
    if not cleanup_success:
        print("❌ 정돈 작업 실패. 백업에서 복원을 고려해주세요.")
        return False
    
    # 4단계: 최종 검증
    print("\n" + "=" * 60)
    print("✅ 4단계: 최종 검증")
    print("=" * 60)
    
    final_check = run_command(
        "python safety_check_before_cleanup.py",
        "최종 시스템 검증"
    )
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 정돈 작업 완료 요약")
    print("=" * 60)
    
    if safety_check and backup_success and cleanup_success and final_check:
        print("🎉 모든 단계가 성공적으로 완료되었습니다!")
        print("✅ 시스템이 깔끔하게 정돈되었습니다.")
        print("✅ 모든 기능이 정상적으로 작동합니다.")
        
        print("\n📋 정돈된 항목들:")
        print("- 중복된 AI 서비스 파일들")
        print("- 중복된 문서 파일들")
        print("- 중복된 테스트 파일들")
        
        print("\n📁 백업 위치:")
        print("- backup/ 디렉토리에 안전하게 보관됨")
        print("- 복원이 필요한 경우 restore_backup.py 실행")
        
        return True
    else:
        print("⚠️ 일부 단계에서 문제가 발생했습니다.")
        print("❌ 백업에서 복원을 고려해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
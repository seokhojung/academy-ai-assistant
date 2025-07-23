#!/usr/bin/env python3
"""
강의 데이터 상세 확인 스크립트
"""

import asyncio
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.lecture import Lecture

async def check_lecture_data():
    """강의 데이터 상세 확인"""
    
    print("=" * 60)
    print("📖 강의 데이터 상세 확인")
    print("=" * 60)
    
    try:
        session = next(get_session())
        
        # 강의 데이터 확인
        lectures = session.query(Lecture).all()
        print(f"\n📖 강의 데이터: {len(lectures)}개")
        
        if lectures:
            print("\n전체 강의 목록:")
            for i, lecture in enumerate(lectures, 1):
                print(f"  {i}. {lecture.title}")
                print(f"     - 과목: {lecture.subject}")
                print(f"     - 학년: {lecture.grade}")
                print(f"     - 일정: {lecture.schedule}")
                print(f"     - 강의실: {lecture.classroom}")
                print(f"     - 최대 학생 수: {lecture.max_students}")
                print(f"     - 현재 학생 수: {lecture.current_students}")
                print(f"     - 수강료: {lecture.tuition_fee}")
                print(f"     - 활성화: {lecture.is_active}")
                print(f"     - 생성일: {lecture.created_at}")
                print()
        else:
            print("❌ 강의 데이터가 없습니다!")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_lecture_data()) 
#!/usr/bin/env python3
"""
구체적인 AI 질문 테스트 스크립트
"""

import asyncio
from app.ai.services.ai_service_factory import AIServiceFactory
from app.core.config import settings
from app.core.database import get_session

async def test_specific_questions():
    """구체적인 질문으로 AI 테스트"""
    
    print("=" * 60)
    print("🤖 구체적인 AI 질문 테스트")
    print("=" * 60)
    
    try:
        # AI 서비스 생성
        ai_service = AIServiceFactory.create_service(settings.current_ai_config)
        
        # 데이터베이스 세션 생성
        session = next(get_session())
        
        # 테스트 질문들
        test_questions = [
            "학생 목록을 보여주세요",
            "강사는 몇 명인가요?",
            "수학 과목 교재가 몇 개 있나요?",
            "현재 등록된 학생 중 고등학생은 몇 명인가요?",
            "가장 최근에 등록된 학생 3명의 이름을 알려주세요"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 질문 {i}: {question}")
            print("-" * 40)
            
            try:
                response = await ai_service.generate_response(question, session)
                print(f"🤖 응답: {response}")
                
                # JSON 파싱 시도
                import json
                try:
                    parsed = json.loads(response)
                    if parsed.get('type') == 'table_data':
                        print("✅ 테이블 데이터 형식 응답")
                    elif parsed.get('type') == 'text':
                        print("✅ 텍스트 형식 응답")
                    else:
                        print("⚠️ 알 수 없는 응답 형식")
                except json.JSONDecodeError:
                    print("❌ JSON 파싱 실패")
                    
            except Exception as e:
                print(f"❌ 오류: {e}")
            
            print()
        
        session.close()
        
    except Exception as e:
        print(f"❌ AI 서비스 생성 실패: {e}")

if __name__ == "__main__":
    asyncio.run(test_specific_questions()) 
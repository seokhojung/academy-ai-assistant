import asyncio
import requests
import json
from typing import List, Tuple, Dict, Any

class AISystemTester:
    """AI 시스템 테스터"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_cases = self._get_test_cases()
    
    def _get_test_cases(self) -> List[Tuple[str, str, str]]:
        """테스트 케이스 정의"""
        return [
            ("학생 목록 보여줘", "table_data", "학생 데이터가 포함되어야 함"),
            ("강사 목록 보여줘", "table_data", "강사 데이터가 포함되어야 함"),
            ("안녕하세요", "text", "자연스러운 인사말이어야 함"),
            ("전체 현황", "table_data", "모든 데이터가 포함되어야 함"),
        ]
    
    async def test_new_system(self):
        """새로운 AI 시스템 테스트"""
        print("🧪 새로운 AI 시스템 테스트 시작...")
        
        for message, expected_type, description in self.test_cases:
            print(f"\n📝 테스트: {message}")
            print(f"   기대: {expected_type} - {description}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/ai/chat/test",
                    json={"message": message},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("response", "")
                    
                    # JSON 형식 검증
                    try:
                        parsed = json.loads(ai_response)
                        response_type = parsed.get("type", "unknown")
                        
                        if response_type == expected_type:
                            print(f"   ✅ 성공: {response_type}")
                        else:
                            print(f"   ❌ 실패: 기대 {expected_type}, 실제 {response_type}")
                        
                        # 데이터 검증
                        if self._validate_data_consistency(parsed):
                            print(f"   ✅ 데이터 일관성 검증 통과")
                        else:
                            print(f"   ⚠️ 데이터 일관성 검증 실패")
                            
                    except json.JSONDecodeError:
                        print(f"   ❌ JSON 파싱 실패")
                        
                else:
                    print(f"   ❌ HTTP 오류: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ 테스트 오류: {e}")
        
        print("\n🏁 테스트 완료")
    
    def _validate_data_consistency(self, parsed_response: Dict[str, Any]) -> bool:
        """데이터 일관성 검증"""
        response_str = json.dumps(parsed_response, ensure_ascii=False)
        
        # 금지된 내용 검증
        forbidden_content = ["html", "markdown", "```", "응답:", "답변:"]
        for content in forbidden_content:
            if content in response_str.lower():
                return False
        
        return True

if __name__ == "__main__":
    tester = AISystemTester()
    asyncio.run(tester.test_new_system()) 
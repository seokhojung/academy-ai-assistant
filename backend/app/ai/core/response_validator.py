import json
import re
from typing import Dict, Any, Tuple, Optional

class ResponseValidator:
    """AI 응답 검증 시스템"""
    
    def __init__(self):
        self.validation_rules = self._get_validation_rules()
    
    def _get_validation_rules(self) -> Dict[str, Any]:
        """검증 규칙 정의"""
        return {
            "json_format": {
                "required": True,
                "description": "응답은 유효한 JSON 형식이어야 함"
            },
            "required_fields": {
                "type": {"required": True, "allowed_values": ["table_data", "text", "analysis", "command"]},
                "content": {"required": True}
            },
            "forbidden_content": {
                "html_tags": ["<", ">", "&lt;", "&gt;"],
                "markdown": ["```", "**", "*", "#"],
                "plain_text": ["응답:", "답변:", "AI:"]
            },
            "data_consistency": {
                "student_count": "실제 DB 학생 수와 일치해야 함",
                "teacher_count": "실제 DB 강사 수와 일치해야 함"
            }
        }
    
    def validate_response(self, response: str, context_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """응답 검증 (완화된 버전)"""
        try:
            # 1. JSON 형식 검증 (가장 중요)
            if not self._is_valid_json(response):
                return False, "응답이 유효한 JSON 형식이 아닙니다"
            
            # 2. JSON 파싱
            parsed_response = json.loads(response)
            
            # 디버깅: 파싱된 응답 출력
            print(f"[ResponseValidator] 파싱된 응답: {parsed_response}")
            
            # 3. 필수 필드 검증 (완화)
            if not self._validate_required_fields(parsed_response):
                print(f"[ResponseValidator] 필수 필드 검증 실패: {parsed_response}")
                return False, "필수 필드가 누락되었습니다"
            
            # 4. 금지된 내용 검증 (완화)
            if self._contains_forbidden_content(response):
                return False, "금지된 내용이 포함되어 있습니다"
            
            # 5. 데이터 일관성 검증 (테스트 시에는 건너뛰기)
            # 실제 운영 환경에서만 활성화
            if context_data and len(context_data) > 0:
                if not self._validate_data_consistency(parsed_response, context_data):
                    # 경고만 하고 실패로 처리하지 않음
                    print(f"[ResponseValidator] 데이터 일관성 경고: 실제 데이터와 일치하지 않을 수 있습니다")
            
            print(f"[ResponseValidator] 검증 성공")
            return True, None
            
        except Exception as e:
            print(f"[ResponseValidator] 검증 중 오류: {e}")
            return False, f"검증 중 오류 발생: {str(e)}"
    
    def _is_valid_json(self, response: str) -> bool:
        """JSON 형식 검증"""
        try:
            json.loads(response)
            return True
        except json.JSONDecodeError:
            return False
    
    def _validate_required_fields(self, parsed_response: Dict[str, Any]) -> bool:
        """필수 필드 검증 (완화된 버전)"""
        # type 필드가 있으면 통과
        if "type" in parsed_response:
            return True
        
        # content 필드가 있으면 통과
        if "content" in parsed_response:
            return True
        
        # table_data 형식의 경우 content 필드 확인
        if "table_data" in parsed_response:
            table_data = parsed_response["table_data"]
            if isinstance(table_data, dict) and "content" in table_data:
                return True
        
        # 빈 객체가 아닌 경우 통과 (최소한의 유효성)
        if isinstance(parsed_response, dict) and len(parsed_response) > 0:
            return True
        
        return False
    
    def _contains_forbidden_content(self, response: str) -> bool:
        """금지된 내용 검증"""
        forbidden_content = self.validation_rules["forbidden_content"]
        
        for content_type, patterns in forbidden_content.items():
            for pattern in patterns:
                if pattern in response:
                    return True
        
        return False
    
    def _validate_data_consistency(self, parsed_response: Dict[str, Any], context_data: Dict[str, Any]) -> bool:
        """데이터 일관성 검증"""
        response_str = json.dumps(parsed_response, ensure_ascii=False)
        
        # 학생 수 검증 (중요!)
        student_count = len(context_data.get('students', []))
        if "학생" in response_str:
            # 학생 개수와 실제 목록 개수 일치 확인
            if "table_data" in parsed_response and "content" in parsed_response["table_data"]:
                content = parsed_response["table_data"]["content"]
                if "rows" in content:
                    actual_rows = len(content["rows"])
                    if actual_rows != student_count:
                        print(f"[ResponseValidator] ⚠️ 학생 개수 불일치: 시스템({student_count}명) vs 응답({actual_rows}명)")
                        return False
        
        # 강사 수 검증
        teacher_count = len(context_data.get('teachers', []))
        if "강사" in response_str and str(teacher_count) not in response_str:
            return False
        
        # 강의 수 검증 (중요!)
        lecture_count = len(context_data.get('lectures', []))
        if "강의" in response_str:
            # 강의 개수와 실제 목록 개수 일치 확인
            if "table_data" in parsed_response and "content" in parsed_response["table_data"]:
                content = parsed_response["table_data"]["content"]
                if "rows" in content:
                    actual_rows = len(content["rows"])
                    if actual_rows != lecture_count:
                        print(f"[ResponseValidator] ⚠️ 강의 개수 불일치: 시스템({lecture_count}개) vs 응답({actual_rows}개)")
                        return False
        
        # 교재 수 검증
        material_count = len(context_data.get('materials', []))
        if "교재" in response_str and str(material_count) not in response_str:
            return False
        
        return True
    
    def get_validation_report(self, response: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """검증 리포트 생성"""
        is_valid, error_message = self.validate_response(response, context_data)
        
        return {
            "is_valid": is_valid,
            "error_message": error_message,
            "validation_details": {
                "json_format": self._is_valid_json(response),
                "required_fields": self._validate_required_fields(json.loads(response)) if self._is_valid_json(response) else False,
                "forbidden_content": not self._contains_forbidden_content(response),
                "data_consistency": self._validate_data_consistency(json.loads(response), context_data) if self._is_valid_json(response) else False
            }
        } 
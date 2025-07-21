import { AIResponse, TableData, AnalysisData, CommandData, CRUDCommand } from '@/types/ai';

/**
 * AI 응답 텍스트를 파싱하여 구조화된 데이터로 변환
 */
export function parseAIResponse(responseText: string): AIResponse | AIResponse[] {
  try {
    // 여러 JSON 블록이 있는지 확인 (```json ... ``` 형태)
    const jsonBlocks = responseText.match(/```json\s*(\{[\s\S]*?\})\s*```/g);
    
    if (jsonBlocks && jsonBlocks.length > 1) {
      // 여러 JSON 블록이 있는 경우
      const responses: AIResponse[] = [];
      
      for (const block of jsonBlocks) {
        const jsonMatch = block.match(/```json\s*(\{[\s\S]*?\})\s*```/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[1]);
          if (parsed.type && parsed.content) {
            responses.push(parsed as AIResponse);
          }
        }
      }
      
      return responses.length > 0 ? responses : {
        type: 'text',
        content: responseText
      };
    }
    
    // 단일 JSON 응답인지 확인 (더 정확한 패턴)
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        const parsed = JSON.parse(jsonMatch[0]);
        
        // 타입 검증
        if (parsed.type && parsed.content) {
          return parsed as AIResponse;
        }
      } catch (jsonError) {
        console.warn('JSON 매치 파싱 실패:', jsonError);
      }
    }
    
    // 백엔드에서 자동 CRUD 처리 후 반환된 JSON 형식 확인
    if (responseText.trim().startsWith('{') && responseText.trim().endsWith('}')) {
      try {
        const parsed = JSON.parse(responseText);
        if (parsed.type && parsed.content) {
          console.log('백엔드 JSON 응답 파싱 성공:', parsed);
          return parsed as AIResponse;
        }
      } catch (backendJsonError) {
        console.warn('백엔드 JSON 파싱 실패:', backendJsonError);
      }
    }
    
    // JSON이 아니거나 유효하지 않은 경우 텍스트로 처리
    return {
      type: 'text',
      content: responseText
    };
  } catch (error) {
    console.warn('AI 응답 파싱 실패:', error);
    console.log('파싱 실패한 응답:', responseText);
    
    // 백엔드에서 자동 CRUD 처리 후 JSON 형식으로 반환된 경우
    if (responseText.includes('"type":') && responseText.includes('"content":')) {
      try {
        // JSON 블록 추출 시도
        const jsonMatch = responseText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          if (parsed.type && parsed.content) {
            console.log('JSON 블록에서 파싱 성공:', parsed);
            return parsed as AIResponse;
          }
        }
      } catch (jsonError) {
        console.warn('JSON 블록 파싱도 실패:', jsonError);
      }
    }
    
    return {
      type: 'text',
      content: responseText
    };
  }
}

/**
 * AI 응답이 테이블 데이터인지 확인
 */
export function isTableData(response: AIResponse): response is AIResponse & { content: TableData } {
  return response.type === 'table_data';
}

/**
 * AI 응답이 분석 데이터인지 확인
 */
export function isAnalysisData(response: AIResponse): response is AIResponse & { content: AnalysisData } {
  return response.type === 'analysis';
}

/**
 * AI 응답이 명령 데이터인지 확인
 */
export function isCommandData(response: AIResponse): response is AIResponse & { content: CommandData } {
  return response.type === 'command';
}

/**
 * AI 응답이 CRUD 명령인지 확인
 */
export function isCRUDCommand(response: AIResponse): response is AIResponse & { content: CRUDCommand } {
  return response.type === 'crud_command';
}

/**
 * AI 응답이 텍스트인지 확인
 */
export function isTextData(response: AIResponse): response is AIResponse & { content: string } {
  return response.type === 'text';
}

/**
 * 테이블 데이터를 안전하게 검증
 */
export function validateTableData(data: any): TableData | null {
  if (!data || typeof data !== 'object') return null;
  
  const { headers, rows } = data;
  
  if (!Array.isArray(headers) || !Array.isArray(rows)) {
    return null;
  }
  
  // 모든 행이 헤더와 같은 길이인지 확인
  const headerLength = headers.length;
  const isValidRows = rows.every(row => Array.isArray(row) && row.length === headerLength);
  
  if (!isValidRows) {
    return null;
  }
  
  return {
    title: data.title || '',
    headers,
    rows,
    footer: data.footer || ''
  };
}

/**
 * AI 응답을 안전하게 렌더링할 수 있는 형태로 변환
 */
export function sanitizeAIResponse(response: AIResponse): AIResponse {
  switch (response.type) {
    case 'table_data':
      const validatedTable = validateTableData(response.content);
      if (validatedTable) {
        return {
          ...response,
          content: validatedTable
        };
      }
      // 테이블 데이터가 유효하지 않으면 텍스트로 변환
      return {
        type: 'text',
        content: '테이블 데이터를 표시할 수 없습니다.'
      };
    
    case 'text':
      return {
        ...response,
        content: String(response.content)
      };
    
    default:
      return response;
  }
} 
import { AIResponse, TableData, AnalysisData, CommandData, CRUDCommand } from '@/types/ai';

/**
 * AI 응답 텍스트를 파싱하여 구조화된 데이터로 변환
 */
export function parseAIResponse(responseText: string): AIResponse | AIResponse[] {
  console.log('[AI Utils] 파싱 시작:', responseText.substring(0, 200) + '...');
  
  try {
    // 1. 순수 JSON인지 먼저 확인 (가장 일반적인 경우)
    if (responseText.trim().startsWith('{') && responseText.trim().endsWith('}')) {
      try {
        const parsed = JSON.parse(responseText);
        console.log('[AI Utils] 순수 JSON 파싱 성공:', parsed);
        
        // text 타입 내부에 table_data가 있는지 확인
        if (parsed.type === 'text' && typeof parsed.content === 'string') {
          console.log('[AI Utils] text 타입 내부 확인 중...');
          try {
            const innerContent = JSON.parse(parsed.content);
            if (innerContent.table_data && innerContent.table_data.type === 'table_data') {
              console.log('[AI Utils] text 내부의 table_data 발견, 변환:', innerContent.table_data);
              return innerContent.table_data as AIResponse;
            }
          } catch (innerError) {
            console.log('[AI Utils] text 내부 파싱 실패, 원본 유지');
          }
        }
        
        if (parsed.type && parsed.content) {
          console.log('[AI Utils] 유효한 AI 응답 구조 확인됨');
          return parsed as AIResponse;
        }
      } catch (jsonError) {
        console.warn('[AI Utils] 순수 JSON 파싱 실패:', jsonError);
      }
    }
    
    // 2. 여러 JSON 블록이 있는지 확인 (```json ... ``` 형태)
    const jsonBlocks = responseText.match(/```json\s*(\{[\s\S]*?\})\s*```/g);
    
    if (jsonBlocks && jsonBlocks.length > 1) {
      console.log('[AI Utils] 여러 JSON 블록 발견');
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
    
    // 3. 단일 JSON 블록 확인
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        const parsed = JSON.parse(jsonMatch[0]);
        console.log('[AI Utils] JSON 블록 파싱 성공:', parsed);
        
        // text 타입 내부에 table_data가 있는지 확인
        if (parsed.type === 'text' && typeof parsed.content === 'string') {
          console.log('[AI Utils] JSON 블록 내 text 타입 확인 중...');
          try {
            const innerContent = JSON.parse(parsed.content);
            if (innerContent.table_data && innerContent.table_data.type === 'table_data') {
              console.log('[AI Utils] JSON 블록 내 text 내부의 table_data 발견, 변환:', innerContent.table_data);
              return innerContent.table_data as AIResponse;
            }
          } catch (innerError) {
            console.log('[AI Utils] JSON 블록 내 text 내부 파싱 실패, 원본 유지');
          }
        }
        
        if (parsed.type && parsed.content) {
          return parsed as AIResponse;
        }
      } catch (jsonError) {
        console.warn('[AI Utils] JSON 블록 파싱 실패:', jsonError);
      }
    }
    
    // 4. JSON이 아니거나 유효하지 않은 경우 텍스트로 처리
    console.log('[AI Utils] JSON이 아닌 텍스트로 처리');
    return {
      type: 'text',
      content: responseText
    };
  } catch (error) {
    console.warn('[AI Utils] AI 응답 파싱 실패:', error);
    console.log('[AI Utils] 파싱 실패한 응답:', responseText);
    
    // 5. 마지막 시도: JSON 패턴이 있는지 확인
    if (responseText.includes('"type":') && responseText.includes('"content":')) {
      try {
        const jsonMatch = responseText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          
          // text 타입 내부에 table_data가 있는지 확인
          if (parsed.type === 'text' && typeof parsed.content === 'string') {
            console.log('[AI Utils] 마지막 시도에서 text 타입 확인 중...');
            try {
              const innerContent = JSON.parse(parsed.content);
              if (innerContent.table_data && innerContent.table_data.type === 'table_data') {
                console.log('[AI Utils] 마지막 시도에서 text 내부의 table_data 발견, 변환:', innerContent.table_data);
                return innerContent.table_data as AIResponse;
              }
            } catch (innerError) {
              console.log('[AI Utils] 마지막 시도에서 text 내부 파싱 실패, 원본 유지');
            }
          }
          
          if (parsed.type && parsed.content) {
            console.log('[AI Utils] 마지막 시도 성공:', parsed);
            return parsed as AIResponse;
          }
        }
      } catch (jsonError) {
        console.warn('[AI Utils] 마지막 시도도 실패:', jsonError);
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
  console.log('[AI Utils] validateTableData 시작:', data);
  
  if (!data || typeof data !== 'object') {
    console.log('[AI Utils] 데이터가 객체가 아님');
    return null;
  }
  
  const { headers, rows } = data;
  console.log('[AI Utils] headers:', headers);
  console.log('[AI Utils] rows:', rows);
  
  if (!Array.isArray(headers) || !Array.isArray(rows)) {
    console.log('[AI Utils] headers 또는 rows가 배열이 아님');
    return null;
  }
  
  // 모든 행이 헤더와 같은 길이인지 확인
  const headerLength = headers.length;
  const isValidRows = rows.every(row => Array.isArray(row) && row.length === headerLength);
  
  console.log('[AI Utils] headerLength:', headerLength);
  console.log('[AI Utils] isValidRows:', isValidRows);
  
  if (!isValidRows) {
    console.log('[AI Utils] 행 길이가 헤더와 일치하지 않음');
    return null;
  }
  
  const result = {
    title: data.title || '',
    headers,
    rows,
    footer: data.footer || ''
  };
  
  console.log('[AI Utils] 테이블 데이터 검증 성공:', result);
  return result;
}

/**
 * AI 응답을 안전하게 렌더링할 수 있는 형태로 변환
 */
export function sanitizeAIResponse(response: AIResponse): AIResponse {
  console.log('[AI Utils] sanitizeAIResponse 시작:', response.type);
  console.log('[AI Utils] 원본 응답:', response);
  
  switch (response.type) {
    case 'table_data':
      console.log('[AI Utils] 테이블 데이터 검증 시작');
      const validatedTable = validateTableData(response.content);
      console.log('[AI Utils] 검증된 테이블:', validatedTable);
      
      if (validatedTable) {
        console.log('[AI Utils] 테이블 데이터 검증 성공');
        return {
          ...response,
          content: validatedTable
        };
      }
      // 테이블 데이터가 유효하지 않으면 텍스트로 변환
      console.log('[AI Utils] 테이블 데이터 검증 실패 - 텍스트로 변환');
      return {
        type: 'text',
        content: '테이블 데이터를 표시할 수 없습니다.'
      };
    
    case 'text':
      console.log('[AI Utils] 텍스트 데이터 처리');
      return {
        ...response,
        content: String(response.content)
      };
    
    default:
      console.log('[AI Utils] 기본 처리:', response.type);
      return response;
  }
} 
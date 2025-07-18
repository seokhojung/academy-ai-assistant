import { ApiClient } from '../commands';

// 실제 API 클라이언트 구현
export class HttpApiClient implements ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl;
  }

  async updateEntity(entityType: string, id: number, data: any): Promise<any> {
    console.log(`[API] PUT ${this.baseUrl}/${entityType}/${id}`);
    console.log(`[API] 전송 데이터:`, data);
    console.log(`[API] 데이터 타입:`, typeof data);
    
    const response = await fetch(`${this.baseUrl}/${entityType}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    console.log(`[API] 응답 상태:`, response.status, response.statusText);

    if (!response.ok) {
      // 더 상세한 에러 정보 제공
      let errorMessage = `Failed to update ${entityType} ${id}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        console.log(`[API] 에러 데이터:`, errorData);
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            // Pydantic 검증 에러의 경우
            const validationErrors = errorData.detail.map((err: any) => 
              `${err.loc?.join('.') || 'unknown'}: ${err.msg}`
            ).join(', ');
            errorMessage = `데이터 검증 실패: ${validationErrors}`;
          } else {
            errorMessage += ` - ${errorData.detail}`;
          }
        }
      } catch (e) {
        // JSON 파싱 실패 시 기본 메시지 사용
        console.log(`[API] JSON 파싱 실패:`, e);
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    console.log(`[API] 성공 응답:`, result);
    return result;
  }

  async createEntity(entityType: string, data: any): Promise<any> {
    console.log(`[API] POST ${this.baseUrl}/${entityType}/`);
    console.log(`[API] 전송 데이터:`, data);
    
    const response = await fetch(`${this.baseUrl}/${entityType}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    console.log(`[API] 응답 상태:`, response.status, response.statusText);

    if (!response.ok) {
      let errorMessage = `Failed to create ${entityType}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        console.log(`[API] 에러 데이터:`, errorData);
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            const validationErrors = errorData.detail.map((err: any) => 
              `${err.loc?.join('.') || 'unknown'}: ${err.msg}`
            ).join(', ');
            errorMessage = `데이터 검증 실패: ${validationErrors}`;
          } else {
            errorMessage += ` - ${errorData.detail}`;
          }
        }
      } catch (e) {
        console.log(`[API] JSON 파싱 실패:`, e);
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    console.log(`[API] 성공 응답:`, result);
    return result;
  }

  async deleteEntity(entityType: string, id: number): Promise<any> {
    const response = await fetch(`${this.baseUrl}/${entityType}/${id}/hard`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Failed to delete ${entityType} ${id}: ${response.statusText}`);
    }

    // 204 No Content 응답의 경우 빈 객체 반환
    if (response.status === 204) {
      return { success: true };
    }

    // JSON 응답이 있는 경우에만 파싱
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return { success: true };
  }

  async getEntities(entityType: string): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/${entityType}/`, {
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch ${entityType}: ${response.statusText}`);
    }

    const data = await response.json();
    return data[entityType] || data;
  }
}

// 싱글톤 인스턴스
export const apiClient = new HttpApiClient(); 
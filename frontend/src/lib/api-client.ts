import { ApiClient } from '../commands';

// 실제 API 클라이언트 구현
export class HttpApiClient implements ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl;
  }

  // 인증 토큰 가져오기
  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('authToken');
      if (token) {
        // 토큰 유효성 간단 체크 (JWT 형식 확인)
        const parts = token.split('.');
        if (parts.length === 3) {
          try {
            // 토큰 만료 시간 확인 (선택적)
            const payload = JSON.parse(atob(parts[1]));
            const exp = payload.exp;
            if (exp && Date.now() >= exp * 1000) {
              console.log('[API] 토큰 만료됨, 삭제');
              localStorage.removeItem('authToken');
              return null;
            }
          } catch (e) {
            console.log('[API] 토큰 파싱 오류:', e);
          }
        }
      }
      return token;
    }
    return null;
  }

  // 기본 헤더 설정
  private getHeaders(): HeadersInit {
    const token = this.getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    console.log(`[API] 인증 토큰 상태:`, token ? `존재함 (${token.substring(0, 20)}...)` : '없음');
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  }

  async updateEntity(entityType: string, id: number, data: any): Promise<any> {
    console.log(`[API] PUT ${this.baseUrl}/${entityType}/${id}`);
    console.log(`[API] 전송 데이터:`, data);
    console.log(`[API] 데이터 타입:`, typeof data);
    
    const response = await fetch(`${this.baseUrl}/${entityType}/${id}`, {
      method: 'PUT',
      headers: this.getHeaders(),
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
      headers: this.getHeaders(),
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
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to delete ${entityType} ${id}: ${response.statusText}`);
    }

    return await response.json();
  }

  async executeCRUD(command: any): Promise<any> {
    console.log(`[API] POST ${this.baseUrl}/ai/execute-crud`);
    console.log(`[API] CRUD 명령:`, command);
    
    const response = await fetch(`${this.baseUrl}/ai/execute-crud`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(command),
    });

    console.log(`[API] 응답 상태:`, response.status, response.statusText);

    if (!response.ok) {
      let errorMessage = `CRUD 실행 실패: ${response.statusText}`;
      try {
        const errorData = await response.json();
        console.log(`[API] 에러 데이터:`, errorData);
        if (errorData.detail) {
          errorMessage += ` - ${errorData.detail}`;
        }
        
        // 인증 오류인 경우 관리자 API로 재시도
        if (response.status === 401 || response.status === 403) {
          console.log(`[API] 인증 오류 감지, 관리자 API로 재시도`);
          return await this.executeCRUDAdmin(command);
        }
      } catch (e) {
        console.log(`[API] JSON 파싱 실패:`, e);
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    console.log(`[API] CRUD 성공 응답:`, result);
    return result;
  }

  async executeCRUDAdmin(command: any): Promise<any> {
    console.log(`[API] POST ${this.baseUrl}/ai/execute-crud/admin (관리자 API)`);
    console.log(`[API] CRUD 명령:`, command);
    
    const response = await fetch(`${this.baseUrl}/ai/execute-crud/admin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(command),
    });

    console.log(`[API] 관리자 API 응답 상태:`, response.status, response.statusText);

    if (!response.ok) {
      let errorMessage = `관리자 CRUD 실행 실패: ${response.statusText}`;
      try {
        const errorData = await response.json();
        console.log(`[API] 관리자 API 에러 데이터:`, errorData);
        if (errorData.detail) {
          errorMessage += ` - ${errorData.detail}`;
        }
      } catch (e) {
        console.log(`[API] 관리자 API JSON 파싱 실패:`, e);
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    console.log(`[API] 관리자 CRUD 성공 응답:`, result);
    return result;
  }

  async getEntities(entityType: string): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/${entityType}/`, {
      headers: {
        ...this.getHeaders(),
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
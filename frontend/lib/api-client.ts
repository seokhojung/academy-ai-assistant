import { AIResponse, ChatResponse } from '../src/types/ai';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        // 응답 본문을 읽어서 더 자세한 에러 정보 제공
        const errorText = await response.text();
        let errorMessage = `HTTP error! status: ${response.status}`;
        
        try {
          const errorData = JSON.parse(errorText);
          console.log('백엔드 에러 응답:', errorData);
          
          if (errorData.detail) {
            // detail이 객체인 경우 처리
            if (typeof errorData.detail === 'object') {
              // Pydantic 검증 오류인 경우
              if (Array.isArray(errorData.detail)) {
                const errors = errorData.detail.map((err: any) => 
                  `${err.loc?.join('.') || 'unknown'}: ${err.msg}`
                ).join(', ');
                errorMessage = `검증 오류: ${errors}`;
              } else {
                errorMessage = JSON.stringify(errorData.detail);
              }
            } else {
              errorMessage = errorData.detail;
            }
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else {
            errorMessage = JSON.stringify(errorData);
          }
        } catch (parseError) {
          // JSON 파싱 실패 시 원본 텍스트 사용
          if (errorText) {
            errorMessage = errorText;
          }
        }
        
        throw new Error(errorMessage);
      }

      // 응답이 비어있는지 확인
      const responseText = await response.text();
      
      if (!responseText || responseText.trim() === '') {
        // 빈 응답인 경우 성공으로 처리
        return {
          data: null as T,
          success: true,
        };
      }

      // JSON 파싱 시도
      let data;
      try {
        data = JSON.parse(responseText);
      } catch (jsonError) {
        console.warn('Failed to parse JSON response:', responseText);
        // JSON이 아닌 경우에도 성공으로 처리 (DELETE 요청 등)
        return {
          data: null as T,
          success: true,
        };
      }
      
      return {
        data,
        success: true,
      };
    } catch (error) {
      console.error('API request failed:', error);
      
      return {
        data: null as T,
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // 학생 관련 API
  async getStudents() {
    const response = await this.request('/api/v1/students/');
    const data: any = response.data;
    // 백엔드에서 data.students로 내려오므로, 항상 배열만 반환
    return {
      ...response,
      data: Array.isArray(data && data.students) ? data.students : [],
    };
  }

  async createStudent(studentData: any) {
    return this.request('/api/v1/students/', {
      method: 'POST',
      body: JSON.stringify(studentData),
    });
  }

  async updateStudent(id: number, studentData: any) {
    return this.request(`/api/v1/students/${id}`, {
      method: 'PUT',
      body: JSON.stringify(studentData),
    });
  }

  async deleteStudent(id: number) {
    return this.request(`/api/v1/students/${id}`, {
      method: 'DELETE',
    });
  }

  async deleteStudentHard(id: number) {
    return this.request(`/api/v1/students/${id}/hard`, {
      method: 'DELETE',
    });
  }

  // 강사 관련 API (인증 필요)
  async getTeachersWithAuth(token: string) {
    return this.request('/api/v1/teachers/', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  // 강사 관련 API (인증 없음 - 테스트용)
  async getTeachers() {
    const response = await this.request('/api/v1/teachers/');
    const data: any = response.data;
    return {
      ...response,
      data: Array.isArray(data && data.teachers) ? data.teachers : [],
    };
  }

  async createTeacher(teacherData: any) {
    return this.request('/api/v1/teachers/', {
      method: 'POST',
      body: JSON.stringify(teacherData),
    });
  }

  async updateTeacher(id: number, teacherData: any) {
    return this.request(`/api/v1/teachers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(teacherData),
    });
  }

  async deleteTeacher(id: number) {
    return this.request(`/api/v1/teachers/${id}`, {
      method: 'DELETE',
    });
  }

  // 교재 관련 API
  async getMaterials() {
    const response = await this.request('/api/v1/materials/');
    const data: any = response.data;
    return {
      ...response,
      data: Array.isArray(data && data.materials) ? data.materials : [],
    };
  }

  async createMaterial(materialData: any) {
    return this.request('/api/v1/materials/', {
      method: 'POST',
      body: JSON.stringify(materialData),
    });
  }

  async updateMaterial(id: number, materialData: any) {
    return this.request(`/api/v1/materials/${id}`, {
      method: 'PUT',
      body: JSON.stringify(materialData),
    });
  }

  async deleteMaterial(id: number) {
    return this.request(`/api/v1/materials/${id}`, {
      method: 'DELETE',
    });
  }

  // 강의 관련 API
  async getLectures() {
    const response = await this.request('/api/v1/lectures/');
    const data: any = response.data;
    return {
      ...response,
      data: Array.isArray(data && data.lectures) ? data.lectures : [],
    };
  }

  async createLecture(lectureData: any) {
    return this.request('/api/v1/lectures/', {
      method: 'POST',
      body: JSON.stringify(lectureData),
    });
  }

  async updateLecture(id: number, lectureData: any) {
    return this.request(`/api/v1/lectures/${id}`, {
      method: 'PUT',
      body: JSON.stringify(lectureData),
    });
  }

  async deleteLecture(id: number) {
    return this.request(`/api/v1/lectures/${id}`, {
      method: 'DELETE',
    });
  }

  // AI 채팅 API (인증 필요)
  async sendChatMessage(message: string, token: string): Promise<ApiResponse<ChatResponse>> {
    return this.request<ChatResponse>('/api/v1/ai/chat', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
    });
  }

  // AI 채팅 API (테스트용, 인증 없음)
  async sendChatMessageTest(message: string): Promise<ApiResponse<ChatResponse>> {
    return this.request<ChatResponse>('/api/v1/ai/chat/test', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  // 헬스 체크
  async healthCheck() {
    return this.request('/health');
  }

  // 사용자 컬럼 설정 관련 API
  async getColumnSettings(pageName: string) {
    return this.request(`/api/v1/users/column-settings/${pageName}`);
  }

  async updateColumnSettings(pageName: string, settings: {
    visible_columns: string[];
    hidden_columns: string[];
    column_order: string[];
  }) {
    return this.request(`/api/v1/users/column-settings/${pageName}`, {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }
};

export const apiClient = new ApiClient();
export default apiClient; 
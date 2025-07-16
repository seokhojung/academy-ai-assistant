// API 클라이언트 설정
const API_BASE = process.env.NODE_ENV === 'development' 
  ? '/api'  // 개발 환경: 프록시 사용
  : process.env.NEXT_PUBLIC_API_URL || 'https://academy-ai-assistant.onrender.com';  // 배포 환경: Render API URL

// API 응답 타입
interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

// API 에러 클래스
class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// 인증 토큰 가져오기
const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('authToken');
  }
  return null;
};

// 기본 헤더 설정
const getHeaders = (): HeadersInit => {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

// API 요청 함수
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const config: RequestInit = {
    headers: getHeaders(),
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.message || `HTTP ${response.status}`,
        response.status,
        errorData
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      error instanceof Error ? error.message : 'Network error',
      0
    );
  }
}

// API 클라이언트
export const apiClient = {
  // GET 요청
  async get<T>(endpoint: string): Promise<T> {
    return apiRequest<T>(endpoint, { method: 'GET' });
  },

  // POST 요청
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return apiRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  // PUT 요청
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return apiRequest<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  // DELETE 요청
  async delete<T>(endpoint: string): Promise<T> {
    return apiRequest<T>(endpoint, { method: 'DELETE' });
  },

  // PATCH 요청
  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return apiRequest<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  },
};

// 학생 관련 API
export const studentsApi = {
  getAll: () => apiClient.get('/v1/students/'),
  getById: (id: number) => apiClient.get(`/v1/students/${id}`),
  create: (data: any) => apiClient.post('/v1/students/', data),
  update: (id: number, data: any) => apiClient.put(`/v1/students/${id}`, data),
  delete: (id: number) => apiClient.delete(`/v1/students/${id}`),
};

// 강사 관련 API
export const teachersApi = {
  getAll: () => apiClient.get('/v1/teachers/'),
  getById: (id: number) => apiClient.get(`/v1/teachers/${id}`),
  create: (data: any) => apiClient.post('/v1/teachers/', data),
  update: (id: number, data: any) => apiClient.put(`/v1/teachers/${id}`, data),
  delete: (id: number) => apiClient.delete(`/v1/teachers/${id}`),
};

// 교재 관련 API
export const materialsApi = {
  getAll: () => apiClient.get('/v1/materials/'),
  getById: (id: number) => apiClient.get(`/v1/materials/${id}`),
  create: (data: any) => apiClient.post('/v1/materials/', data),
  update: (id: number, data: any) => apiClient.put(`/v1/materials/${id}`, data),
  delete: (id: number) => apiClient.delete(`/v1/materials/${id}`),
};

// AI 관련 API
export const aiApi = {
  chat: (message: string) => apiClient.post('/v1/ai/chat', { message }),
  analyze: (data: any) => apiClient.post('/v1/ai/analyze', data),
  command: (command: string) => apiClient.post('/v1/ai/command', { command }),
};

// 인증 관련 API
export const authApi = {
  login: (credentials: any) => apiClient.post('/v1/auth/login', credentials),
  logout: () => apiClient.post('/v1/auth/logout'),
  refresh: (token: string) => apiClient.post('/v1/auth/refresh', { token }),
};

export { ApiError }; 
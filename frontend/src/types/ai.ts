// AI 응답 관련 타입 정의

export interface TableData {
  title?: string;
  headers: string[];
  rows: string[][];
  footer?: string;
}

export interface AnalysisData {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  progressScore: number;
}

export interface CommandData {
  commandType: 'student' | 'teacher' | 'material' | 'tuition';
  action: 'get' | 'create' | 'update' | 'delete' | 'list';
  target: string;
  filters: Record<string, any>;
  parameters: Record<string, any>;
}

export interface CRUDCommand {
  action: 'create' | 'update' | 'delete';
  entity: 'student' | 'teacher' | 'material' | 'lecture';
  target: {
    identifier: string;
    field?: string;
    value?: any;
  };
  confirmation: string;
  requires_confirmation: boolean;
}

export interface AIResponse {
  type: 'table_data' | 'text' | 'analysis' | 'command' | 'crud_command';
  content: TableData | string | AnalysisData | CommandData | CRUDCommand;
  summary?: string;
  recommendations?: string[];
  metadata?: {
    timestamp: string;
    processingTime: number;
    dataSource: string;
  };
}

// API 응답 타입
export interface ChatResponse {
  response: AIResponse;
  user_id?: number;
  status?: string;
  debug_info?: any;
}

// 채팅 메시지 타입
export interface ChatMessage {
  id: string;
  content: string | AIResponse;
  isUser: boolean;
  timestamp: Date;
}

// 테이블 스타일 옵션
export interface TableStyleOptions {
  striped?: boolean;
  hover?: boolean;
  bordered?: boolean;
  responsive?: boolean;
  size?: 'sm' | 'md' | 'lg';
} 
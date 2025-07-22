import React from 'react';
import { Bot, User } from 'lucide-react';
import { AIResponse, ChatMessage } from '@/types/ai';
import { isTableData, isTextData, isCRUDCommand, parseAIResponse, sanitizeAIResponse } from '@/lib/ai-utils';
import DataTable from '@/components/ui/DataTable';
import { apiClient } from '@/lib/api-client';

interface AIChatMessageProps {
  message: ChatMessage;
}

const AIChatMessage: React.FC<AIChatMessageProps> = ({ message }) => {
  const renderContent = () => {
    console.log('[AIChatMessage] renderContent 시작');
    console.log('[AIChatMessage] message.isUser:', message.isUser);
    console.log('[AIChatMessage] message.content 타입:', typeof message.content);
    
    if (message.isUser) {
      // 사용자 메시지는 단순 텍스트로 렌더링
      console.log('[AIChatMessage] 사용자 메시지 렌더링');
      return <span className="whitespace-pre-line">{message.content as string}</span>;
    }

    // AI 메시지 처리
    let aiResponse: AIResponse | AIResponse[];
    
    if (typeof message.content === 'string') {
      // 문자열인 경우 파싱 시도
      console.log('[AIChatMessage] 원본 메시지:', message.content.substring(0, 200) + '...');
      aiResponse = parseAIResponse(message.content);
      console.log('[AIChatMessage] 파싱된 응답:', aiResponse);
    } else {
      // 이미 AIResponse 객체인 경우
      console.log('[AIChatMessage] 이미 AIResponse 객체:', message.content);
      aiResponse = message.content;
    }

    // 여러 응답이 있는 경우
    if (Array.isArray(aiResponse)) {
      console.log('[AIChatMessage] 여러 응답 처리:', aiResponse.length);
      return (
        <div className="space-y-4">
          {aiResponse.map((response, index) => {
            const sanitizedResponse = sanitizeAIResponse(response);
            return (
              <div key={index} className="border-t border-gray-200 dark:border-gray-700 pt-4 first:border-t-0 first:pt-0">
                {renderSingleResponse(sanitizedResponse)}
              </div>
            );
          })}
        </div>
      );
    }

    // 단일 응답 처리
    console.log('[AIChatMessage] 단일 응답 처리 시작');
    const sanitizedResponse = sanitizeAIResponse(aiResponse);
    console.log('[AIChatMessage] sanitizedResponse:', sanitizedResponse);
    return renderSingleResponse(sanitizedResponse);
  };

  const renderSingleResponse = (response: AIResponse) => {
    console.log('[AIChatMessage] 렌더링할 응답 타입:', response.type);
    console.log('[AIChatMessage] 응답 전체:', response);
    
    switch (response.type) {
      case 'table_data':
        console.log('[AIChatMessage] 테이블 데이터 렌더링 시작');
        return <TableMessage data={response as AIResponse & { content: any }} />;
      
      case 'text':
        console.log('[AIChatMessage] 텍스트 데이터 렌더링');
        return <TextMessage data={response as AIResponse & { content: string }} />;
      
      case 'analysis':
        console.log('[AIChatMessage] 분석 데이터 렌더링');
        return <AnalysisMessage data={response as AIResponse & { content: any }} />;
      
      case 'command':
        console.log('[AIChatMessage] 명령 데이터 렌더링');
        return <CommandMessage data={response as AIResponse & { content: any }} />;
      
      case 'crud_command':
        // CRUD 명령은 백엔드에서 자동 처리되므로 텍스트로 표시
        console.log('[AIChatMessage] CRUD 명령 처리');
        return <TextMessage data={{ type: 'text', content: '데이터 수정을 처리 중입니다...' } as AIResponse & { content: string }} />;
      
      default:
        console.log('[AIChatMessage] 알 수 없는 응답 형식:', response.type);
        return <TextMessage data={{ type: 'text', content: '알 수 없는 응답 형식입니다.' } as AIResponse & { content: string }} />;
    }
  };

  return (
    <div
      className={`max-w-[75%] px-4 py-2 rounded-2xl shadow-md text-sm
        ${message.isUser
          ? 'bg-gradient-to-tr from-blue-100 to-indigo-100 dark:from-blue-900 dark:to-indigo-900 text-gray-900 dark:text-white rounded-br-md'
          : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-100 rounded-bl-md'}
      `}
    >
      <div className="flex items-center gap-2 mb-2">
        {message.isUser ? (
          <User className="w-4 h-4 text-blue-500 dark:text-blue-300" />
        ) : (
          <Bot className="w-4 h-4 text-indigo-500 dark:text-indigo-300" />
        )}
        <span className="font-medium">
          {message.isUser ? '나' : 'AI'}
        </span>
      </div>
      <div className="space-y-2">
        {renderContent()}
      </div>
    </div>
  );
};

// 테이블 메시지 컴포넌트
const TableMessage: React.FC<{ data: AIResponse & { content: any } }> = ({ data }) => {
  console.log('[TableMessage] 테이블 데이터:', data);
  console.log('[TableMessage] content:', data.content);
  
  return (
    <div className="space-y-3">
      {data.content.title && (
        <h3 className="font-semibold text-gray-900 dark:text-gray-100">
          {data.content.title}
        </h3>
      )}
      <DataTable 
        data={data.content} 
        styleOptions={{ 
          striped: false, 
          hover: true, 
          bordered: true, 
          responsive: true 
        }}
      />
      {data.summary && (
        <p className="text-gray-600 dark:text-gray-400 text-sm">
          {data.summary}
        </p>
      )}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="mt-3">
          <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
            권장사항:
          </h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
            {data.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

// 텍스트 메시지 컴포넌트
const TextMessage: React.FC<{ data: AIResponse & { content: string } }> = ({ data }) => {
  return (
    <div className="space-y-2">
      <span className="whitespace-pre-line">{data.content}</span>
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
          <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
            권장사항:
          </h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
            {data.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

// 분석 메시지 컴포넌트
const AnalysisMessage: React.FC<{ data: AIResponse & { content: any } }> = ({ data }) => {
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
          <h4 className="font-medium text-green-800 dark:text-green-200 mb-2">
            강점
          </h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-green-700 dark:text-green-300">
            {data.content.strengths?.map((strength: string, index: number) => (
              <li key={index}>{strength}</li>
            ))}
          </ul>
        </div>
        <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
          <h4 className="font-medium text-red-800 dark:text-red-200 mb-2">
            개선점
          </h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-red-700 dark:text-red-300">
            {data.content.weaknesses?.map((weakness: string, index: number) => (
              <li key={index}>{weakness}</li>
            ))}
          </ul>
        </div>
      </div>
      {data.content.recommendations && (
        <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
          <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">
            권장사항
          </h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-blue-700 dark:text-blue-300">
            {data.content.recommendations.map((rec: string, index: number) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
      {data.content.progressScore !== undefined && (
        <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
          <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">
            진행도 점수
          </h4>
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${data.content.progressScore}%` }}
              />
            </div>
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {data.content.progressScore}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

// 명령 메시지 컴포넌트
const CommandMessage: React.FC<{ data: AIResponse & { content: any } }> = ({ data }) => {
  return (
    <div className="space-y-3">
      <div className="bg-yellow-50 dark:bg-yellow-900/20 p-3 rounded-lg">
        <h4 className="font-medium text-yellow-800 dark:text-yellow-200 mb-2">
          명령 분석 결과
        </h4>
        <div className="space-y-2 text-sm text-yellow-700 dark:text-yellow-300">
          <p><strong>명령 유형:</strong> {data.content.commandType}</p>
          <p><strong>액션:</strong> {data.content.action}</p>
          <p><strong>대상:</strong> {data.content.target}</p>
        </div>
      </div>
      {data.recommendations && (
        <div className="mt-3">
          <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
            다음 단계:
          </h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
            {data.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};



export default AIChatMessage; 
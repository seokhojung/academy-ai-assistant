'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/use-toast';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { aiApi } from '../../lib/api';
import { parseAIResponse, isCRUDCommand } from '../../lib/ai-utils';
import { apiClient } from '../../lib/api-client';
import AIChatMessage from './AIChatMessage';
import { ChatMessage } from '@/types/ai';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  isLoading?: boolean;
}

interface AIChatBoxProps {
  className?: string;
}

export default function AIChatBox({ 
  className = ""
}: AIChatBoxProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 초기 환영 메시지
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        content: '안녕하세요! AI 어시스턴트입니다. 학생/강사/교재/강의의 관리에 대해 질문해보세요.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      isUser: true,
      timestamp: new Date()
    };

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: '',
      isUser: false,
      timestamp: new Date(),
      isLoading: true
    };

    const newMessages = [...messages, userMessage, loadingMessage];
    setMessages(newMessages);
    setInputMessage('');
    setIsLoading(true);

    try {
      // 실제 AI API 사용
      const response = await aiApi.chat(inputMessage) as any;
      // 로딩 메시지 제거
      const messagesWithoutLoading = newMessages.filter(msg => !msg.isLoading);

      if (response && response.response) {
        // AI 응답 파싱
        const aiResponseText = typeof response.response === 'string' ? response.response : 'AI 응답을 받았습니다.';
        
        // CRUD 명령 처리
        try {
          const parsedResponse = parseAIResponse(aiResponseText);
          // 배열인 경우 첫 번째 요소 사용
          const response = Array.isArray(parsedResponse) ? parsedResponse[0] : parsedResponse;
          
          if (isCRUDCommand(response)) {
            // CRUD 명령 실행
            console.log('CRUD 명령 감지:', response);
            
            try {
              const crudResult = await apiClient.executeCRUD(response.content);
              console.log('CRUD 실행 결과:', crudResult);
              
              // 성공 메시지 추가
              const successMessage: Message = {
                id: (Date.now() + 3).toString(),
                content: `✅ ${(response as any).confirmation || '데이터가 성공적으로 수정되었습니다.'}`,
                isUser: false,
                timestamp: new Date()
              };
              
              const aiMessage: Message = {
                id: (Date.now() + 2).toString(),
                content: aiResponseText,
                isUser: false,
                timestamp: new Date()
              };
              
              const finalMessages = [...messagesWithoutLoading, aiMessage, successMessage];
              setMessages(finalMessages);
              
              toast({
                title: "수정 완료",
                description: "데이터가 성공적으로 수정되었습니다.",
              });
              
              return; // CRUD 처리 완료
            } catch (crudError) {
              console.error('CRUD 실행 실패:', crudError);
              
              // 실패 메시지 추가
              const errorMessage: Message = {
                id: (Date.now() + 3).toString(),
                content: `❌ 데이터 수정에 실패했습니다: ${crudError instanceof Error ? crudError.message : '알 수 없는 오류'}`,
                isUser: false,
                timestamp: new Date()
              };
              
              const aiMessage: Message = {
                id: (Date.now() + 2).toString(),
                content: aiResponseText,
                isUser: false,
                timestamp: new Date()
              };
              
              const finalMessages = [...messagesWithoutLoading, aiMessage, errorMessage];
              setMessages(finalMessages);
              
              toast({
                title: "수정 실패",
                description: "데이터 수정에 실패했습니다.",
                variant: "destructive",
              });
              
              return; // CRUD 처리 완료
            }
          }
        } catch (parseError) {
          console.log('CRUD 명령이 아닙니다:', parseError);
        }
        
        // 일반 AI 응답
        const aiMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: aiResponseText,
          isUser: false,
          timestamp: new Date()
        };
        
        const finalMessages = [...messagesWithoutLoading, aiMessage];
        setMessages(finalMessages);
      } else {
        // 응답이 없는 경우
        const errorMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: '죄송합니다. 현재 응답을 생성할 수 없습니다. 잠시 후 다시 시도해주세요.',
          isUser: false,
          timestamp: new Date()
        };
        
        const finalMessages = [...messagesWithoutLoading, errorMessage];
        setMessages(finalMessages);
        
        toast({
          title: "응답 실패",
          description: "AI 응답을 받지 못했습니다.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('AI API 호출 실패:', error);
      
      // 로딩 메시지 제거
      const messagesWithoutLoading = newMessages.filter(msg => !msg.isLoading);
      
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: '죄송합니다. 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.',
        isUser: false,
        timestamp: new Date()
      };
      
      const finalMessages = [...messagesWithoutLoading, errorMessage];
      setMessages(finalMessages);
      
      toast({
        title: "오류 발생",
        description: "AI 서비스에 연결할 수 없습니다.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className={`relative flex flex-col h-[800px] md:h-[880px] w-full bg-white/60 dark:bg-gray-900/60 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-inner overflow-hidden ${className}`}>
      
      {/* 채팅 메시지 영역 */}
      <div
        ref={messagesEndRef}
        className="flex-1 overflow-y-auto px-4 py-6 space-y-3 scrollbar-thin scrollbar-thumb-blue-200 dark:scrollbar-thumb-blue-900"
        style={{scrollbarWidth: 'thin'}}
      >
        {messages.map((message) => {
          // ChatMessage 형식으로 변환
          const chatMessage: ChatMessage = {
            id: message.id,
            content: message.content,
            isUser: message.isUser,
            timestamp: message.timestamp
          };
          
          return (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              {message.isLoading ? (
                <div
                  className={`max-w-[75%] px-4 py-2 rounded-2xl shadow-md bg-white/80 dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-100 ${message.isUser ? 'rounded-br-md' : 'rounded-bl-md'}`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Bot className="w-4 h-4 text-indigo-500 dark:text-indigo-300" />
                    <span className="font-medium text-sm">AI</span>
                  </div>
                  <div className="text-sm">
                    <div className="flex items-center gap-2">
                      <Bot className="w-4 h-4 text-indigo-500 dark:text-indigo-300 animate-bounce" />
                      <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
                      <span>AI가 답변 중...</span>
                    </div>
                  </div>
                </div>
              ) : (
                <AIChatMessage message={chatMessage} />
              )}
            </div>
          );
        })}
      </div>
      
      {/* 입력창 영역 */}
      <form
        className="flex items-center gap-2 px-4 py-3 bg-white/80 dark:bg-gray-900/80 border-t border-gray-200 dark:border-gray-700"
        onSubmit={e => { e.preventDefault(); handleSendMessage(); }}
      >
        <Input
          className="flex-1 rounded-full shadow-sm border border-gray-300 dark:border-gray-700 focus:ring-2 focus:ring-blue-400 dark:focus:ring-blue-600 bg-white/90 dark:bg-gray-800/90 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
          placeholder="메시지를 입력하세요..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={isLoading}
          autoFocus
        />
        <Button
          type="submit"
          className="rounded-full p-2 bg-gradient-to-tr from-blue-500 to-indigo-500 text-white shadow-md hover:from-blue-600 hover:to-indigo-600 focus:ring-2 focus:ring-blue-400 dark:focus:ring-blue-600"
          disabled={isLoading || !inputMessage.trim()}
          size="icon"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
        </Button>
      </form>
    </div>
  );
} 
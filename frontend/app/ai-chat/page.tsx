'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '../../lib/api-client';
import { Send, Bot, User, Loader2, Trash2, Download, Upload } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { aiApi } from '../../lib/api';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  isLoading?: boolean;
}

interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

export default function AIChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [showSessions, setShowSessions] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 로컬 스토리지에서 채팅 세션 로드
  useEffect(() => {
    const savedSessions = localStorage.getItem('chatSessions');
    if (savedSessions) {
      const sessions = JSON.parse(savedSessions);
      setChatSessions(sessions);
      
      // 마지막 세션이 있으면 로드
      if (sessions.length > 0) {
        const lastSession = sessions[sessions.length - 1];
        setCurrentSessionId(lastSession.id);
        setMessages(lastSession.messages);
      } else {
        createNewSession();
      }
    } else {
      createNewSession();
    }
  }, []);

  // 채팅 세션 저장
  const saveChatSessions = (sessions: ChatSession[]) => {
    localStorage.setItem('chatSessions', JSON.stringify(sessions));
    setChatSessions(sessions);
  };

  // 새 세션 생성
  const createNewSession = () => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: '새 대화',
      messages: [],
      createdAt: new Date()
    };
    
    const welcomeMessage: Message = {
      id: 'welcome',
      content: '안녕하세요! 저는 학원 관리 시스템의 AI 어시스턴트입니다. 학생 관리, 강사 관리, 교재 관리 등에 대해 질문해주세요. 무엇을 도와드릴까요?',
      isUser: false,
      timestamp: new Date()
    };
    
    newSession.messages = [welcomeMessage];
    setMessages([welcomeMessage]);
    setCurrentSessionId(newSession.id);
    
    const updatedSessions = [...chatSessions, newSession];
    saveChatSessions(updatedSessions);
  };

  // 세션 로드
  const loadSession = (sessionId: string) => {
    const session = chatSessions.find(s => s.id === sessionId);
    if (session) {
      setMessages(session.messages);
      setCurrentSessionId(sessionId);
      setShowSessions(false);
    }
  };

  // 세션 삭제
  const deleteSession = (sessionId: string) => {
    const updatedSessions = chatSessions.filter(s => s.id !== sessionId);
    saveChatSessions(updatedSessions);
    
    if (currentSessionId === sessionId) {
      if (updatedSessions.length > 0) {
        loadSession(updatedSessions[0].id);
      } else {
        createNewSession();
      }
    }
  };

  // 세션 제목 업데이트
  const updateSessionTitle = (sessionId: string, title: string) => {
    const updatedSessions = chatSessions.map(s => 
      s.id === sessionId ? { ...s, title } : s
    );
    saveChatSessions(updatedSessions);
  };

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
    
    // 세션 업데이트
    const updatedSessions = chatSessions.map(s => 
      s.id === currentSessionId 
        ? { ...s, messages: newMessages, title: inputMessage.slice(0, 30) + '...' }
        : s
    );
    saveChatSessions(updatedSessions);
    
    setInputMessage('');
    setIsLoading(true);

    try {
      // 실제 AI API 사용
      const response = await aiApi.chat(inputMessage) as any;
      // 로딩 메시지 제거
      const messagesWithoutLoading = newMessages.filter(msg => !msg.isLoading);

      if (response && response.response) {
        const aiMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: typeof response.response === 'string' ? response.response : 'AI 응답을 받았습니다.',
          isUser: false,
          timestamp: new Date()
        };
        
        const finalMessages = [...messagesWithoutLoading, aiMessage];
        setMessages(finalMessages);
        // 세션 업데이트
        const finalUpdatedSessions = chatSessions.map(s => 
          s.id === currentSessionId 
            ? { ...s, messages: finalMessages }
            : s
        );
        saveChatSessions(finalUpdatedSessions);
      } else {
        // API 오류인 경우 임시 응답 제공
        const tempResponse = generateTempResponse(inputMessage);
        const aiMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: tempResponse,
          isUser: false,
          timestamp: new Date()
        };
        
        const finalMessages = [...messagesWithoutLoading, aiMessage];
        setMessages(finalMessages);
        // 세션 업데이트
        const finalUpdatedSessions = chatSessions.map(s => 
          s.id === currentSessionId 
            ? { ...s, messages: finalMessages }
            : s
        );
        saveChatSessions(finalUpdatedSessions);
        toast({
          title: "AI 응답",
          description: "현재 AI 서비스 점검 중입니다. 임시 응답을 제공합니다.",
          variant: "info",
        });
      }
    } catch (error) {
      // 로딩 메시지 제거
      const messagesWithoutLoading = messages.filter(msg => !msg.isLoading);
      
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: '죄송합니다. 현재 AI 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.',
        isUser: false,
        timestamp: new Date()
      };
      
      const finalMessages = [...messagesWithoutLoading, errorMessage];
      setMessages(finalMessages);
      
      // 세션 업데이트
      const finalUpdatedSessions = chatSessions.map(s => 
        s.id === currentSessionId 
          ? { ...s, messages: finalMessages }
          : s
      );
      saveChatSessions(finalUpdatedSessions);
      
      toast({
        title: "연결 오류",
        description: "AI 서비스 연결에 실패했습니다.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 임시 응답 생성 함수 (인증 문제 해결 전까지 사용)
  const generateTempResponse = (message: string): string => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('학생') || lowerMessage.includes('student')) {
      return '학생 관리 기능에 대해 안내드리겠습니다. 학생 등록, 정보 수정, 출석 관리 등을 할 수 있습니다. 대시보드에서 "학생 관리" 메뉴를 클릭하시면 됩니다.';
    } else if (lowerMessage.includes('강사') || lowerMessage.includes('teacher')) {
      return '강사 관리 기능에 대해 안내드리겠습니다. 강사 등록, 스케줄 관리, 강의 현황 등을 확인할 수 있습니다. 대시보드에서 "강사 관리" 메뉴를 클릭하시면 됩니다.';
    } else if (lowerMessage.includes('교재') || lowerMessage.includes('material')) {
      return '교재 관리 기능에 대해 안내드리겠습니다. 교재 등록, 재고 관리, 교재별 학생 현황 등을 확인할 수 있습니다. 대시보드에서 "교재 관리" 메뉴를 클릭하시면 됩니다.';
    } else if (lowerMessage.includes('수강료') || lowerMessage.includes('tuition')) {
      return '수강료 관리 기능에 대해 안내드리겠습니다. 수강료 납부 현황, 미납 학생 관리, 납부 일정 등을 확인할 수 있습니다.';
    } else if (lowerMessage.includes('안녕') || lowerMessage.includes('hello')) {
      return '안녕하세요! 학원 관리 시스템에 오신 것을 환영합니다. 무엇을 도와드릴까요?';
    } else {
      return '죄송합니다. 현재 AI 서비스 점검 중입니다. 학생 관리, 강사 관리, 교재 관리 등에 대해 질문해주시면 도움을 드리겠습니다.';
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // 채팅 내보내기
  const exportChat = () => {
    const chatData = {
      session: chatSessions.find(s => s.id === currentSessionId),
      exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${currentSessionId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="flex gap-6 h-[calc(100vh-200px)]">
        {/* 사이드바 - 채팅 세션 목록 */}
        <div className="w-80 flex-shrink-0">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">대화 목록</h2>
                <div className="flex gap-2">
                  <Button
                    onClick={createNewSession}
                    size="sm"
                    variant="outline"
                  >
                    새 대화
                  </Button>
                  <Button
                    onClick={() => setShowSessions(!showSessions)}
                    size="sm"
                    variant="outline"
                  >
                    {showSessions ? '접기' : '펼치기'}
                  </Button>
                </div>
              </div>
              
              {showSessions && (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {chatSessions.map((session) => (
                    <div
                      key={session.id}
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        currentSessionId === session.id
                          ? 'bg-blue-100 border border-blue-300'
                          : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                      onClick={() => loadSession(session.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{session.title}</p>
                          <p className="text-xs text-gray-500">
                            {session.createdAt.toLocaleDateString()}
                          </p>
                        </div>
                        <Button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteSession(session.id);
                          }}
                          size="sm"
                          variant="ghost"
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* 메인 채팅 영역 */}
        <div className="flex-1 flex flex-col">
          <motion.div 
            className="mb-4"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold flex items-center gap-2">
                  <Bot className="w-8 h-8 text-blue-600" />
                  AI 채팅
                </h1>
                <p className="text-gray-600">AI와 대화하여 학습에 도움을 받아보세요.</p>
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={exportChat}
                  variant="outline"
                  size="sm"
                >
                  <Download className="w-4 h-4 mr-2" />
                  내보내기
                </Button>
              </div>
            </div>
          </motion.div>

          <Card className="flex-1">
            <CardContent className="p-4 h-full flex flex-col">
              <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                <AnimatePresence>
                  {messages.map((message, index) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className="flex items-start gap-2 max-w-[70%]">
                        {!message.isUser && (
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                            <Bot className="w-4 h-4 text-blue-600" />
                          </div>
                        )}
                        
                        <div
                          className={`p-3 rounded-lg ${
                            message.isUser
                              ? 'bg-blue-500 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          {message.isLoading ? (
                            <div className="flex items-center gap-2">
                              <Loader2 className="w-4 h-4 animate-spin" />
                              <p className="text-sm">AI가 응답을 생성하고 있습니다...</p>
                            </div>
                          ) : (
                            <>
                              <div 
                                className="text-sm whitespace-pre-wrap [&_table]:w-full [&_table]:border-collapse [&_table]:my-2 [&_th]:border [&_th]:border-gray-300 [&_th]:px-2 [&_th]:py-1 [&_th]:bg-gray-50 [&_th]:text-left [&_td]:border [&_td]:border-gray-300 [&_td]:px-2 [&_td]:py-1 [&_tr:nth-child(even)]:bg-gray-50"
                                dangerouslySetInnerHTML={{ __html: message.content }}
                              />
                              <p className={`text-xs mt-1 ${
                                message.isUser ? 'text-blue-100' : 'text-gray-500'
                              }`}>
                                {message.timestamp.toLocaleTimeString()}
                              </p>
                            </>
                          )}
                        </div>
                        
                        {message.isUser && (
                          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <User className="w-4 h-4 text-white" />
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                
                <div ref={messagesEndRef} />
              </div>

              <div className="flex gap-2">
                <Input
                  value={inputMessage}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="메시지를 입력하세요... (Enter로 전송)"
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  className="px-4"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 
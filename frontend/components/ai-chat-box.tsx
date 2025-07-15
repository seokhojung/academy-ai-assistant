"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/input";
import { Bot, User, Send, Loader2 } from "lucide-react";
import { apiClient } from "../lib/api-client";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  isLoading?: boolean;
}

export default function AIChatBox() {
  const [messages, setMessages] = useState<Message[]>([{
    id: "welcome",
    content: "안녕하세요! AI 어시스턴트입니다. 학생/강사/교재/강의의 관리에 대해 질문해보세요.",
    isUser: false,
    timestamp: new Date(),
  }]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      content: input,
      isUser: true,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await apiClient.sendChatMessageTest(userMsg.content);
      setMessages((prev) => [
        ...prev,
        {
          id: `ai-${Date.now()}`,
          content: typeof res.data === 'string' ? res.data : ((res.data as any)?.response) || 'AI 응답을 받았습니다.',
          isUser: false,
          timestamp: new Date(),
        },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          id: `ai-error-${Date.now()}`,
          content: "⚠️ AI 응답에 실패했습니다. 다시 시도해 주세요.",
          isUser: false,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="relative flex flex-col h-[400px] md:h-[440px] w-full bg-white/60 dark:bg-gray-900/60 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-inner overflow-hidden">
      {/* 채팅 메시지 영역 */}
      <div
        ref={chatRef}
        className="flex-1 overflow-y-auto px-4 py-6 space-y-3 scrollbar-thin scrollbar-thumb-blue-200 dark:scrollbar-thumb-blue-900"
        style={{scrollbarWidth: 'thin'}}
      >
        {messages.map((msg, idx) => (
          <div
            key={msg.id}
            className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[75%] px-4 py-2 rounded-2xl shadow-md text-sm whitespace-pre-line
                ${msg.isUser
                  ? 'bg-gradient-to-tr from-blue-100 to-indigo-100 dark:from-blue-900 dark:to-indigo-900 text-gray-900 dark:text-white rounded-br-md'
                  : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-100 rounded-bl-md'}
              `}
            >
              <div className="flex items-center gap-2 mb-1">
                {msg.isUser ? (
                  <User className="w-4 h-4 text-blue-500 dark:text-blue-300" />
                ) : (
                  <Bot className="w-4 h-4 text-indigo-500 dark:text-indigo-300" />
                )}
                <span className="font-medium">
                  {msg.isUser ? '나' : 'AI'}
                </span>
              </div>
              <span>{msg.content}</span>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="max-w-[75%] px-4 py-2 rounded-2xl shadow-md bg-white/80 dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-100 rounded-bl-md flex items-center gap-2">
              <Bot className="w-4 h-4 text-indigo-500 dark:text-indigo-300 animate-bounce" />
              <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
              <span>AI가 답변 중...</span>
            </div>
          </div>
        )}
      </div>
      {/* 입력창 영역 */}
      <form
        className="flex items-center gap-2 px-4 py-3 bg-white/80 dark:bg-gray-900/80 border-t border-gray-200 dark:border-gray-700"
        onSubmit={e => { e.preventDefault(); handleSendMessage(); }}
      >
        <Input
          className="flex-1 rounded-full shadow-sm border border-gray-300 dark:border-gray-700 focus:ring-2 focus:ring-blue-400 dark:focus:ring-blue-600 bg-white/90 dark:bg-gray-800/90 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
          placeholder="메시지를 입력하세요..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={loading}
          autoFocus
        />
        <Button
          type="submit"
          className="rounded-full p-2 bg-gradient-to-tr from-blue-500 to-indigo-500 text-white shadow-md hover:from-blue-600 hover:to-indigo-600 focus:ring-2 focus:ring-blue-400 dark:focus:ring-blue-600"
          disabled={loading || !input.trim()}
          size="icon"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
        </Button>
      </form>
    </div>
  );
} 
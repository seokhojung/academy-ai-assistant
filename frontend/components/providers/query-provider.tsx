'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, useEffect } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // 데이터가 "신선"하다고 간주하는 시간 (5분)
            staleTime: 5 * 60 * 1000,
            // 캐시에 보관하는 시간 (10분) - v5에서는 gcTime
            gcTime: 10 * 60 * 1000,
            // 재시도 횟수
            retry: 1,
            // 윈도우 포커스 시 자동 재요청 비활성화
            refetchOnWindowFocus: false,
            // 네트워크 재연결 시 자동 재요청
            refetchOnReconnect: true,
            // 에러 발생 시 재시도 간격
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
          },
          mutations: {
            // 뮤테이션 재시도 횟수
            retry: 1,
            // 뮤테이션 실패 시 재시도 간격
            retryDelay: 1000,
          },
        },
      })
  );

  // 클라이언트 사이드에서만 실행되도록 보장
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    return <div>Loading...</div>;
  }

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
} 
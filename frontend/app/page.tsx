'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // 인증 토큰 확인
    const token = localStorage.getItem('authToken');
    
    if (token) {
      // 토큰이 있으면 대시보드로
      router.push('/dashboard');
    } else {
      // 토큰이 없으면 로그인으로
      router.push('/login');
    }
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
    </div>
  );
}

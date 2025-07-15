'use client';

import { LoginForm } from '@/components/auth/LoginForm';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  const handleLoginSuccess = (token: string) => {
    // JWT 토큰을 로컬 스토리지에 저장
    localStorage.setItem('authToken', token);
    
    // 대시보드로 리다이렉트
    router.push('/dashboard');
  };

  return <LoginForm onLoginSuccess={handleLoginSuccess} />;
} 
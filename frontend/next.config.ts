import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    typedRoutes: true,
  },
  // 성능 최적화
  compiler: {
    // 프로덕션에서 불필요한 console.log 제거
    removeConsole: process.env.NODE_ENV === 'production',
  },
  // 이미지 최적화
  images: {
    domains: ['localhost', '121.165.240.250'],
  },
  // 개발 환경에서 외부 도메인 허용
  allowedDevOrigins: [
    'http://121.165.240.250:3000',
    'http://121.165.240.250:3001',
    'http://121.165.240.250:3002',
    'http://121.165.240.250:3003',
  ],
  // API 프록시 (CORS 문제 해결)
  async rewrites() {
    const isDevelopment = process.env.NODE_ENV === 'development';
    const backendUrl = isDevelopment 
      ? 'http://localhost:8000' 
      : 'https://academy-ai-assistant.onrender.com';
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
  // 빌드 최적화
  compress: true,
  // 정적 파일 최적화
  generateEtags: false,
  // 개발 서버 최적화
  reactStrictMode: true,
  // 타입 체크 최적화
  typescript: {
    ignoreBuildErrors: false,
  },
  // ESLint 최적화
  eslint: {
    ignoreDuringBuilds: false,
  },
};

export default nextConfig;

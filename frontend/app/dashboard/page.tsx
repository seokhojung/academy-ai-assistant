'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { GlassCard, KPIGrid } from '@/components/ui/glass-card';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { Toaster } from '@/components/ui/toaster';
import { useToast } from '@/hooks/use-toast';
import { Users, GraduationCap, BookOpen, Calendar, Bot } from 'lucide-react';
import { Calendar as CalendarComponent } from '@/components/ui/Calendar';
import { Chart, GradeChart, AttendanceChart } from '@/components/ui/Chart';
import AIChatBox from '../../components/ai-chat-box';

interface DashboardStats {
  students: number;
  teachers: number;
  materials: number;
  activeCourses: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [stats, setStats] = useState<DashboardStats>({
    students: 0,
    teachers: 0,
    materials: 0,
    activeCourses: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // 인증 토큰 확인
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.push('/login');
      return;
    }

    // 대시보드 데이터 로드
    loadDashboardData();
  }, [router]);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // 실제 API 호출로 DB 통계 가져오기
      const [studentsRes, teachersRes, materialsRes, lecturesRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/students/'),
        fetch('http://localhost:8000/api/v1/teachers/'),
        fetch('http://localhost:8000/api/v1/materials/'),
        fetch('http://localhost:8000/api/v1/lectures/')
      ]);

      const studentsData = await studentsRes.json();
      const teachersData = await teachersRes.json();
      const materialsData = await materialsRes.json();
      const lecturesData = await lecturesRes.json();

      // 실제 DB 데이터로 통계 설정
      setStats({
        students: studentsData.total || studentsData.students?.length || 0,
        teachers: teachersData.length || 0,
        materials: materialsData.length || 0,
        activeCourses: lecturesData.total || lecturesData.lectures?.length || 0
      });

      console.log('실제 DB 통계:', {
        students: studentsData.total || studentsData.students?.length || 0,
        teachers: teachersData.length || 0,
        materials: materialsData.length || 0,
        activeCourses: lecturesData.total || lecturesData.lectures?.length || 0
      });

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast({
        title: "데이터 로드 실패",
        description: "대시보드 데이터를 불러오는데 실패했습니다.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    router.push('/login');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* 헤더 */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Academy AI Assistant
            </h1>
            <div className="flex items-center space-x-4">
              <ThemeToggle />
              <Button onClick={handleLogout} variant="outline">
                로그아웃
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Glassmorphism KPI 카드 */}
        <KPIGrid>
          <GlassCard
            title="전체 학생"
            value={`${stats.students}명`}
            description="등록된 학생 수"
            icon={Users}
            trend={{ value: 12, isPositive: true }}
            onClick={() => {
              router.push('/students');
              toast({
                title: "학생 관리 페이지로 이동",
                description: "학생 정보를 확인하고 관리할 수 있습니다.",
                variant: "info",
              });
            }}
          />
          <GlassCard
            title="전체 강사"
            value={`${stats.teachers}명`}
            description="활성 강사 수"
            icon={GraduationCap}
            trend={{ value: 5, isPositive: true }}
            onClick={() => {
              router.push('/teachers');
              toast({
                title: "강사 관리 페이지로 이동",
                description: "강사 정보를 확인하고 관리할 수 있습니다.",
                variant: "info",
              });
            }}
          />
          <GlassCard
            title="교재 종류"
            value={`${stats.materials}종`}
            description="보유 교재 수"
            icon={BookOpen}
            trend={{ value: 3, isPositive: true }}
            onClick={() => {
              router.push('/materials');
              toast({
                title: "교재 관리 페이지로 이동",
                description: "교재 정보를 확인하고 관리할 수 있습니다.",
                variant: "info",
              });
            }}
          />
          <GlassCard
            title="진행 중인 강의"
            value={`${stats.activeCourses}개`}
            description="현재 진행 중인 강의"
            icon={Calendar}
            trend={{ value: 8, isPositive: true }}
            onClick={() => {
              router.push('/lectures');
              toast({
                title: "강의 관리 페이지로 이동",
                description: "강의 정보를 확인하고 관리할 수 있습니다.",
                variant: "info",
              });
            }}
          />
        </KPIGrid>

        {/* AI 어시스턴트 + 채팅창 통합 넓은 카드 */}
        <div className="bg-white/70 dark:bg-gray-900/80 backdrop-blur-xl shadow-xl border border-white/20 rounded-2xl p-8 mt-8 w-full max-w-6xl mx-auto flex flex-col items-stretch">
          <div className="flex items-center gap-4 mb-6">
            <div className="bg-gradient-to-tr from-blue-400 to-indigo-500 rounded-full p-4 shadow-lg">
              <Bot className="w-10 h-10 text-white" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">AI 어시스턴트</div>
              <div className="text-base text-gray-600 dark:text-gray-300">학생/강사/교재/강의 관리, 데이터 질의, 자연어 명령을 도와드립니다.</div>
            </div>
          </div>
          <div className="w-full">
            <AIChatBox />
          </div>
        </div>

        {/* 캘린더 및 차트 섹션 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          {/* 캘린더 */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">수업 일정</h2>
            <CalendarComponent
              events={[
                {
                  id: '1',
                  title: '수학 수업',
                  date: new Date(2025, 0, 15),
                  type: 'class'
                },
                {
                  id: '2',
                  title: '영어 시험',
                  date: new Date(2025, 0, 20),
                  type: 'exam'
                },
                {
                  id: '3',
                  title: '학부모 상담',
                  date: new Date(2025, 0, 25),
                  type: 'event'
                }
              ]}
              onDateSelect={(date) => {
                toast({
                  title: "날짜 선택",
                  description: `${date.toLocaleDateString()} 날짜가 선택되었습니다.`,
                  variant: "info",
                });
              }}
              onEventClick={(event) => {
                toast({
                  title: "이벤트 클릭",
                  description: `${event.title} 이벤트가 선택되었습니다.`,
                  variant: "info",
                });
              }}
            />
          </div>

          {/* 차트 */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">성적 통계</h2>
            <GradeChart
              data={[
                { name: '김철수', grade: 85, value: 85 },
                { name: '이영희', grade: 92, value: 92 },
                { name: '박민수', grade: 78, value: 78 },
                { name: '정수진', grade: 95, value: 95 },
                { name: '최동현', grade: 88, value: 88 }
              ]}
            />
          </div>
        </div>

        {/* 출석률 차트 */}
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md shadow-sm border border-white/20 rounded-xl p-6 mt-8">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">월별 출석률</h2>
          <AttendanceChart
            data={[
              { name: '1월', month: '1월', attendance: 95, value: 95 },
              { name: '2월', month: '2월', attendance: 92, value: 92 },
              { name: '3월', month: '3월', attendance: 88, value: 88 },
              { name: '4월', month: '4월', attendance: 90, value: 90 },
              { name: '5월', month: '5월', attendance: 93, value: 93 },
              { name: '6월', month: '6월', attendance: 89, value: 89 }
            ]}
          />
        </div>
      </main>
      
      {/* Toast 알림 */}
      <Toaster />
    </div>
  );
} 
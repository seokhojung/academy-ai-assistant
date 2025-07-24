import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

// 통계 데이터 타입 정의
export interface StudentStatistics {
  total_students: number;
  active_students: number;
  inactive_students: number;
  grade_distribution: Record<string, number>;
  tuition_stats: {
    total_revenue: number;
    average_tuition: number;
    overdue_count: number;
    recent_registrations: number;
  };
}

export interface LectureStatistics {
  total_lectures: number;
  active_lectures: number;
  inactive_lectures: number;
  subject_distribution: Record<string, number>;
  grade_distribution: Record<string, number>;
  enrollment_stats: {
    total_enrollments: number;
    total_capacity: number;
    average_enrollment: number;
    average_capacity: number;
    enrollment_rate: number;
  };
  revenue_stats: {
    total_revenue: number;
    average_tuition: number;
  };
  popular_lectures: Array<{
    id: number;
    title: string;
    subject: string;
    current_students: number;
    max_students: number;
    enrollment_rate: number;
  }>;
}

export interface TeacherStatistics {
  total_teachers: number;
  active_teachers: number;
  inactive_teachers: number;
  teacher_performance: Array<{
    teacher_id: number;
    teacher_name: string;
    lecture_count: number;
    total_students: number;
    average_enrollment_rate: number;
    total_revenue: number;
  }>;
  subject_teacher_distribution: Record<string, number>;
}

export interface MaterialStatistics {
  total_materials: number;
  active_materials: number;
  inactive_materials: number;
  subject_distribution: Record<string, number>;
  material_usage: Array<{
    material_id: number;
    material_name: string;
    subject: string;
    usage_count: number;
  }>;
}

export interface OverallStatistics {
  summary: {
    total_students: number;
    total_lectures: number;
    total_teachers: number;
    total_materials: number;
    total_revenue: number;
  };
  student_stats: StudentStatistics;
  lecture_stats: LectureStatistics;
  teacher_stats: TeacherStatistics;
  material_stats: MaterialStatistics;
}

// API Base URL 설정
const getApiBaseUrl = (): string => {
  // 브라우저 환경에서는 항상 상대 경로 사용 (Vercel rewrites 활용)
  if (typeof window !== 'undefined') {
    return '/api/v1';
  }
  // 서버 사이드에서는 환경에 따라 결정
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000/api/v1';
  }
  return '/api/v1';
};

// 통계 데이터 페칭 함수들
const fetchStudentStatistics = async (): Promise<StudentStatistics> => {
  const response = await fetch(`${getApiBaseUrl()}/statistics/students`);
  if (!response.ok) {
    throw new Error('학생 통계 조회 실패');
  }
  return response.json();
};

const fetchLectureStatistics = async (): Promise<LectureStatistics> => {
  const response = await fetch(`${getApiBaseUrl()}/statistics/lectures`);
  if (!response.ok) {
    throw new Error('강의 통계 조회 실패');
  }
  return response.json();
};

const fetchTeacherStatistics = async (): Promise<TeacherStatistics> => {
  const response = await fetch(`${getApiBaseUrl()}/statistics/teachers`);
  if (!response.ok) {
    throw new Error('강사 통계 조회 실패');
  }
  return response.json();
};

const fetchMaterialStatistics = async (): Promise<MaterialStatistics> => {
  const response = await fetch(`${getApiBaseUrl()}/statistics/materials`);
  if (!response.ok) {
    throw new Error('교재 통계 조회 실패');
  }
  return response.json();
};

const fetchOverallStatistics = async (): Promise<OverallStatistics> => {
  const response = await fetch(`${getApiBaseUrl()}/statistics/overall`);
  if (!response.ok) {
    throw new Error('전체 통계 조회 실패');
  }
  return response.json();
};

// 통계 데이터 훅들
export const useStudentStatistics = () => {
  return useQuery({
    queryKey: ['statistics', 'students'],
    queryFn: fetchStudentStatistics,
    staleTime: 5 * 60 * 1000, // 5분
    gcTime: 30 * 60 * 1000, // 30분
    refetchOnWindowFocus: false,
    retry: 3,
  });
};

export const useLectureStatistics = () => {
  return useQuery({
    queryKey: ['statistics', 'lectures'],
    queryFn: fetchLectureStatistics,
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 3,
  });
};

export const useTeacherStatistics = () => {
  return useQuery({
    queryKey: ['statistics', 'teachers'],
    queryFn: fetchTeacherStatistics,
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 3,
  });
};

export const useMaterialStatistics = () => {
  return useQuery({
    queryKey: ['statistics', 'materials'],
    queryFn: fetchMaterialStatistics,
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 3,
  });
};

export const useOverallStatistics = () => {
  return useQuery({
    queryKey: ['statistics', 'overall'],
    queryFn: fetchOverallStatistics,
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
    retry: 3,
  });
};

// 통합 통계 훅
export const useAllStatistics = () => {
  const studentStats = useStudentStatistics();
  const lectureStats = useLectureStatistics();
  const teacherStats = useTeacherStatistics();
  const materialStats = useMaterialStatistics();
  const overallStats = useOverallStatistics();

  const isLoading = 
    studentStats.isLoading || 
    lectureStats.isLoading || 
    teacherStats.isLoading || 
    materialStats.isLoading || 
    overallStats.isLoading;

  const error = 
    studentStats.error || 
    lectureStats.error || 
    teacherStats.error || 
    materialStats.error || 
    overallStats.error;

  return {
    studentStats: studentStats.data,
    lectureStats: lectureStats.data,
    teacherStats: teacherStats.data,
    materialStats: materialStats.data,
    overallStats: overallStats.data,
    isLoading,
    error,
    refetch: () => {
      studentStats.refetch();
      lectureStats.refetch();
      teacherStats.refetch();
      materialStats.refetch();
      overallStats.refetch();
    }
  };
}; 
'use client';

import React, { useState, useEffect } from "react";
import DataManagementTable from "../../src/components/data-management/DataManagementTable";
import { GridColDef } from "@mui/x-data-grid";
import { useHistoryManager } from "../../src/hooks/useHistoryManager";
import { EditEntityCommand, AddEntityCommand, DeleteEntityCommand } from "../../src/commands";
import { apiClient } from "../../src/lib/api-client";

interface Teacher {
  id: number;
  name: string;
  email: string;
  phone: string;
  subject: string;
  hourly_rate: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function TeachersPage() {
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [dynamicColumns, setDynamicColumns] = useState<GridColDef[]>([]);
  
  // 히스토리 관리자 사용
  const { executeCommand } = useHistoryManager();

  useEffect(() => {
    fetchTeachers();
  }, []);

  const fetchTeachers = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getEntities('teachers') as any;
      // API 응답이 {"teachers": [...]} 형태이므로 data.teachers로 접근
      const teachersData = data.teachers || data;
      
      // 최신 등록순으로 정렬 (created_at 기준 내림차순)
      const sortedTeachers = Array.isArray(teachersData) 
        ? teachersData.sort((a: Teacher, b: Teacher) => {
            const dateA = new Date(a.created_at).getTime();
            const dateB = new Date(b.created_at).getTime();
            return dateB - dateA; // 최신이 맨 위
          })
        : [];
      
      setTeachers(sortedTeachers);
    } catch (error) {
      console.error('강사 데이터 로드 실패:', error);
      setTeachers([]);
    } finally {
      setIsLoading(false);
    }
  };

  // 기본 DataGrid 컬럼 정의
  const baseTeacherColumns: GridColDef[] = [
    { field: "name", headerName: "이름", width: 170, editable: true },
    { field: "email", headerName: "이메일", width: 240, editable: true },
    { field: "phone", headerName: "전화번호", width: 180, editable: true },
    { field: "subject", headerName: "담당 과목", width: 140, editable: true },
    { field: "hourly_rate", headerName: "시급(원)", width: 120, editable: true, type: "number" },
    { field: "is_active", headerName: "상태", width: 110, editable: true, type: "singleSelect", valueOptions: ["활성", "비활성"] },
    { field: "created_at", headerName: "등록일", width: 140, editable: false }
  ];

  // 동적 컬럼과 기본 컬럼을 결합
  const teacherColumns = [...baseTeacherColumns, ...dynamicColumns];

  // CRUD 함수 - Command Pattern 기반
  const handleRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      // Command Pattern을 사용하여 편집 히스토리 관리
      const editCommand = new EditEntityCommand(
        'teachers',
        newRow.id,
        oldRow,
        newRow, // EditEntityCommand에서 데이터 검증 및 변환 처리
        apiClient,
        (data) => {
          // 로컬 상태 업데이트
          setTeachers(prev => 
            prev.map(teacher => 
              teacher.id === newRow.id ? data : teacher
            )
          );
        }
      );
      
      await executeCommand(editCommand);
      return newRow;
    } catch (e) {
      console.error('업데이트 오류:', e);
      return oldRow;
    }
  };

  const handleAddRow = async () => {
    // 백엔드 스키마에 맞는 데이터 검증 및 변환
    const newTeacher = {
      name: "새 강사",
      email: `teacher${Date.now()}@example.com`,
      phone: null,  // 빈 문자열 대신 null 사용
      subject: "수학",  // 기본값 설정
      hourly_rate: 0,  // 숫자 타입
      is_active: true,
    };
    
    try {
      // Command Pattern을 사용하여 추가 히스토리 관리
      const addCommand = new AddEntityCommand(
        'teachers',
        newTeacher,
        apiClient,
        (data) => {
          // 로컬 상태에 추가 (최신순으로 맨 위에)
          setTeachers(prev => [data, ...prev]);
        },
        (id) => {
          // 로컬 상태에서 제거
          setTeachers(prev => prev.filter(teacher => teacher.id !== id));
        }
      );
      
      await executeCommand(addCommand);
    } catch (error) {
      console.error('추가 오류:', error);
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
      alert(`새 강사 추가 중 오류가 발생했습니다: ${errorMessage}`);
    }
  };

  const handleDeleteRow = async (id: number) => {
    try {
      // 삭제할 강사 데이터 찾기
      const teacherToDelete = teachers.find(teacher => teacher.id === id);
      if (!teacherToDelete) {
        throw new Error("삭제할 강사를 찾을 수 없습니다.");
      }

      // Command Pattern을 사용하여 삭제 히스토리 관리
      const deleteCommand = new DeleteEntityCommand(
        'teachers',
        id,
        teacherToDelete,
        apiClient,
        (id) => {
          // 로컬 상태에서 제거
          setTeachers(prev => prev.filter(teacher => teacher.id !== id));
        },
        (data) => {
          // 로컬 상태에 추가 (복구 시)
          setTeachers(prev => [data, ...prev]);
        }
      );
      
      await executeCommand(deleteCommand);
    } catch (error) {
      console.error('삭제 오류:', error);
      alert('삭제 중 오류가 발생했습니다.');
    }
  };

  // 컬럼 설정 변경 핸들러
  const handleColumnSettingsChange = (visibleColumns: string[], columnOrder: string[], allColumns: GridColDef[]) => {
    // 사용자 정의 컬럼만 추출 (기본 컬럼 제외)
    const customColumns = allColumns.filter(col => 
      !baseTeacherColumns.some(baseCol => baseCol.field === col.field)
    );
    setDynamicColumns(customColumns);
  };

  // 통계 정보 계산
  const total = Array.isArray(teachers) ? teachers.length : 0;
  const active = Array.isArray(teachers) ? teachers.filter(t => t.is_active).length : 0;
  const inactive = Array.isArray(teachers) ? teachers.filter(t => !t.is_active).length : 0;
  const recentRegistration = Array.isArray(teachers) && teachers.length > 0 ? teachers[0].name : undefined;

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">로딩 중...</div>;
  }

  return (
    <DataManagementTable
      entityType="teachers"
      title="강사 관리"
      description="강사 정보를 효율적으로 관리하세요!"
      columns={teacherColumns}
      data={Array.isArray(teachers) ? teachers.map(t => ({ ...t, is_active: t.is_active ? "활성" : "비활성" })) : []}
      onRowUpdate={handleRowUpdate}
      onAddRow={handleAddRow}
      onDeleteRow={handleDeleteRow}
      summaryStats={{ total, active, inactive, recentRegistration }}
      onColumnSettingsChange={handleColumnSettingsChange}
    />
  );
} 
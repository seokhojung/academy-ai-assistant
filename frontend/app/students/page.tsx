'use client';

import React, { useState, useEffect } from "react";
import DataManagementTable from "../../src/components/data-management/DataManagementTable";
import { GridColDef } from "@mui/x-data-grid";
import { useHistoryManager } from "../../src/hooks/useHistoryManager";
import { EditEntityCommand, AddEntityCommand, DeleteEntityCommand } from "../../src/commands";
import { apiClient } from "../../src/lib/api-client";

interface Student {
  id: number;
  name: string;
  email: string;
  phone: string;
  grade: string;
  tuition_fee: number;
  tuition_due_date: string | Date | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [pendingChanges, setPendingChanges] = useState<any[]>([]);
  const [dynamicColumns, setDynamicColumns] = useState<GridColDef[]>([]);
  
  // 히스토리 관리자 사용
  const { executeCommand, clearHistory } = useHistoryManager();

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getEntities('students') as any;
      // API 응답이 {"students": [...]} 형태이므로 data.students로 접근
      const studentsData = data.students || data;
      
      // 최신 등록순으로 정렬 (created_at 기준 내림차순)
      const sortedStudents = Array.isArray(studentsData) 
        ? studentsData.sort((a: Student, b: Student) => {
            const dateA = new Date(a.created_at).getTime();
            const dateB = new Date(b.created_at).getTime();
            return dateB - dateA; // 최신이 맨 위
          })
        : [];
      
      setStudents(sortedStudents);
    } catch (error) {
      console.error('학생 데이터 로드 실패:', error);
      setStudents([]);
    } finally {
      setIsLoading(false);
    }
  };

  // 기본 DataGrid 컬럼 정의
  const baseStudentColumns: GridColDef[] = [
    { field: "name", headerName: "이름", width: 170, editable: true },
    { field: "email", headerName: "이메일", width: 240, editable: true },
    { field: "phone", headerName: "전화번호", width: 180, editable: true },
    { field: "grade", headerName: "학년", width: 100, editable: true },
    { field: "tuition_fee", headerName: "수강료", width: 120, editable: true, type: "number" },
    { field: "tuition_due_date", headerName: "납부일", width: 140, editable: true },
    { field: "is_active", headerName: "상태", width: 110, editable: true, type: "singleSelect", valueOptions: ["활성", "비활성"] },
    { field: "created_at", headerName: "등록일", width: 140, editable: false }
  ];

  // 동적 컬럼과 기본 컬럼을 결합
  const studentColumns = [...baseStudentColumns, ...dynamicColumns];

  // CRUD 함수 - Command Pattern 기반
  const handleRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      // Command Pattern을 사용하여 편집 히스토리 관리
      const editCommand = new EditEntityCommand(
        'students',
        newRow.id,
        oldRow,
        newRow, // EditEntityCommand에서 데이터 검증 및 변환 처리
        apiClient,
        (data) => {
          // 로컬 상태 업데이트
          setStudents(prev => 
            prev.map(student => 
              student.id === newRow.id ? data : student
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
    const newStudent = {
      name: "새 학생",
      email: `student${Date.now()}@example.com`,
      phone: null,  // 빈 문자열 대신 null 사용
      grade: "1학년",
      tuition_fee: 0.0,  // float 타입으로 명시
      tuition_due_date: null,  // 빈 문자열 대신 null 사용 (백엔드에서 Optional[datetime] 처리)
      is_active: true,
    };
    
    try {
      // Command Pattern을 사용하여 추가 히스토리 관리
      const addCommand = new AddEntityCommand(
        'students',
        newStudent,
        apiClient,
        (data) => {
          // 로컬 상태에 추가 (최신순으로 맨 위에)
          setStudents(prev => [data, ...prev]);
        },
        (id) => {
          // 로컬 상태에서 제거
          setStudents(prev => prev.filter(student => student.id !== id));
        }
      );
      
      await executeCommand(addCommand);
    } catch (error) {
      console.error('추가 오류:', error);
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
      alert(`새 학생 추가 중 오류가 발생했습니다: ${errorMessage}`);
    }
  };

  const handleDeleteRow = async (id: number) => {
    try {
      // 삭제할 학생 데이터 찾기
      const studentToDelete = students.find(student => student.id === id);
      if (!studentToDelete) {
        throw new Error("삭제할 학생을 찾을 수 없습니다.");
      }

      // Command Pattern을 사용하여 삭제 히스토리 관리
      const deleteCommand = new DeleteEntityCommand(
        'students',
        id,
        studentToDelete,
        apiClient,
        (id) => {
          // 로컬 상태에서 제거
          setStudents(prev => prev.filter(student => student.id !== id));
        },
        (data) => {
          // 로컬 상태에 추가 (복구 시)
          setStudents(prev => [data, ...prev]);
        }
      );
      
      await executeCommand(deleteCommand);
    } catch (error) {
      console.error('삭제 오류:', error);
      alert('삭제 중 오류가 발생했습니다.');
    }
  };

  const handleSaveAll = async () => {
    // Command Pattern에서는 각 명령이 즉시 실행되므로 별도 저장 로직 불필요
    // 기존 pendingChanges 호환성을 위해 유지
    if (pendingChanges.length === 0) return;
    
    try {
      // 모든 pending changes를 서버에 저장
      for (const change of pendingChanges) {
        await apiClient.updateEntity('students', change.id, change.newData);
      }
      
      // 성공적으로 저장되면 pendingChanges 초기화
      setPendingChanges([]);
      await fetchStudents(); // 데이터 새로고침
      console.log('모든 변경사항 저장 완료');
    } catch (error) {
      console.error('저장 오류:', error);
      alert('저장 중 오류가 발생했습니다.');
    }
  };

  // 컬럼 설정 변경 핸들러
  const handleColumnSettingsChange = (visibleColumns: string[], columnOrder: string[], allColumns: GridColDef[]) => {
    // 사용자 정의 컬럼만 추출 (기본 컬럼 제외)
    const customColumns = allColumns.filter(col => 
      !baseStudentColumns.some(baseCol => baseCol.field === col.field)
    );
    setDynamicColumns(customColumns);
  };

  // 통계 정보 계산 (students가 배열일 때만)
  const total = Array.isArray(students) ? students.length : 0;
  const active = Array.isArray(students) ? students.filter(s => s.is_active).length : 0;
  const inactive = Array.isArray(students) ? students.filter(s => !s.is_active).length : 0;
  const recentRegistration = Array.isArray(students) && students.length > 0 ? students[0].name : undefined;

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">로딩 중...</div>;
  }

  return (
    <DataManagementTable
      entityType="students"
      title="학생 관리"
      description="학생 정보를 효율적으로 관리하세요!"
      columns={studentColumns}
      data={Array.isArray(students) ? students.map(s => ({ ...s, is_active: s.is_active ? "활성" : "비활성" })) : []}
      onRowUpdate={handleRowUpdate}
      onAddRow={handleAddRow}
      onDeleteRow={handleDeleteRow}
      onSaveAll={handleSaveAll}
      pendingChanges={pendingChanges}
      summaryStats={{ total, active, inactive, recentRegistration }}
      onColumnSettingsChange={handleColumnSettingsChange}
    />
  );
} 
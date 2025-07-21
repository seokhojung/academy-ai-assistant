'use client';

import React, { useState, useEffect } from "react";
import DataManagementTable from "../../src/components/data-management/DataManagementTable";
import { GridColDef } from "@mui/x-data-grid";
import { School } from "@mui/icons-material";
import { useHistoryManager } from "../../src/hooks/useHistoryManager";
import { EditEntityCommand, AddEntityCommand, DeleteEntityCommand } from "../../src/commands";
import { apiClient } from "../../src/lib/api-client";

interface Lecture {
  id: number;
  title: string;
  subject: string;
  teacher_id: number | null;
  material_id: number | null;
  grade: string;
  max_students: number;
  current_students: number;
  tuition_fee: number;
  schedule: string;
  classroom: string;
  is_active: boolean;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export default function LecturesPage() {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // 히스토리 관리자 사용
  const { executeCommand } = useHistoryManager();

  useEffect(() => {
    fetchLectures();
  }, []);

  // AI 챗봇에서 데이터 변경 시 자동 갱신
  useEffect(() => {
    const handleDataUpdate = (event: CustomEvent) => {
      const { entity, action } = event.detail;
      if (entity === 'lecture') {
        console.log(`[LecturesPage] AI 챗봇에서 ${action} 감지, 데이터 갱신`);
        fetchLectures();
      }
    };

    window.addEventListener('dataUpdated', handleDataUpdate as EventListener);
    
    return () => {
      window.removeEventListener('dataUpdated', handleDataUpdate as EventListener);
    };
  }, []);

  const fetchLectures = async () => {
    setIsLoading(true);
    try {
      const data = await apiClient.getEntities('lectures') as any;
      const lecturesData = data.lectures || data;
      setLectures(Array.isArray(lecturesData) ? lecturesData : []);
    } catch (error) {
      console.error('강의 데이터 로드 실패:', error);
      setLectures([]);
    } finally {
      setIsLoading(false);
    }
  };

  // DataGrid 컬럼 정의
  const lectureColumns: GridColDef[] = [
    { field: "title", headerName: "강의명", width: 180, editable: true },
    { field: "subject", headerName: "과목", width: 120, editable: true },
    { field: "grade", headerName: "학년", width: 100, editable: true },
    { field: "max_students", headerName: "최대 인원", width: 120, editable: true, type: "number" },
    { field: "current_students", headerName: "현재 인원", width: 120, editable: true, type: "number" },
    { field: "tuition_fee", headerName: "수강료", width: 120, editable: true, type: "number" },
    { field: "schedule", headerName: "스케줄", width: 150, editable: true },
    { field: "classroom", headerName: "강의실", width: 120, editable: true },
    { field: "is_active", headerName: "상태", width: 110, editable: true, type: "singleSelect", valueOptions: ["활성", "비활성"] },
    { field: "created_at", headerName: "등록일", width: 140, editable: false }
  ];

  // CRUD 함수 - Command Pattern 기반
  const handleRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      // Command Pattern을 사용하여 편집 히스토리 관리
      const editCommand = new EditEntityCommand(
        'lectures',
        newRow.id,
        oldRow,
        newRow, // EditEntityCommand에서 데이터 검증 및 변환 처리
        apiClient,
        (data) => {
          // 로컬 상태 업데이트
          setLectures(prev => 
            prev.map(lecture => 
              lecture.id === newRow.id ? data : lecture
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
    const newLecture = {
      title: "새 강의",
      subject: null,  // 빈 문자열 대신 null 사용
      grade: null,    // 빈 문자열 대신 null 사용
      max_students: 20,
      current_students: 0,
      tuition_fee: 0,
      schedule: null, // 빈 문자열 대신 null 사용
      classroom: null, // 빈 문자열 대신 null 사용
      is_active: true,
      description: null // 빈 문자열 대신 null 사용
    };
    
    try {
      // Command Pattern을 사용하여 추가 히스토리 관리
      const addCommand = new AddEntityCommand(
        'lectures',
        newLecture,
        apiClient,
        (data) => {
          // 로컬 상태에 추가 (최신순으로 맨 위에)
          setLectures(prev => [data, ...prev]);
        },
        (id) => {
          // 로컬 상태에서 제거
          setLectures(prev => prev.filter(lecture => lecture.id !== id));
        }
      );
      
      await executeCommand(addCommand);
    } catch (error) {
      console.error('추가 오류:', error);
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
      alert(`새 강의 추가 중 오류가 발생했습니다: ${errorMessage}`);
    }
  };

  const handleDeleteRow = async (id: number) => {
    try {
      // 삭제할 강의 데이터 찾기
      const lectureToDelete = lectures.find(lecture => lecture.id === id);
      if (!lectureToDelete) {
        throw new Error("삭제할 강의를 찾을 수 없습니다.");
      }

      // Command Pattern을 사용하여 삭제 히스토리 관리
      const deleteCommand = new DeleteEntityCommand(
        'lectures',
        id,
        lectureToDelete,
        apiClient,
        (id) => {
          // 로컬 상태에서 제거
          setLectures(prev => prev.filter(lecture => lecture.id !== id));
        },
        (data) => {
          // 로컬 상태에 추가 (복구 시)
          setLectures(prev => [data, ...prev]);
        }
      );
      
      await executeCommand(deleteCommand);
    } catch (error) {
      console.error('삭제 오류:', error);
      alert('삭제 중 오류가 발생했습니다.');
    }
  };

  // 통계 정보 계산
  const total = Array.isArray(lectures) ? lectures.length : 0;
  const active = Array.isArray(lectures) ? lectures.filter(l => l.is_active).length : 0;
  const inactive = Array.isArray(lectures) ? lectures.filter(l => !l.is_active).length : 0;
  const recentRegistration = Array.isArray(lectures) && lectures.length > 0 ? lectures[0].title : undefined;

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">로딩 중...</div>;
  }

  return (
    <DataManagementTable
      entityType="lectures"
      title="강의 관리"
      description="강의 정보를 효율적으로 관리하세요!"
      icon={<School />}
      columns={lectureColumns}
      data={Array.isArray(lectures) ? lectures.map(l => ({ ...l, is_active: l.is_active ? "활성" : "비활성" })) : []}
      onRowUpdate={handleRowUpdate}
      onAddRow={handleAddRow}
      onDeleteRow={handleDeleteRow}
      summaryStats={{ total, active, inactive, recentRegistration }}
    />
  );
} 
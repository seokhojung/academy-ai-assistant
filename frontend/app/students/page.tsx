'use client';

import React, { useState, useEffect } from "react";
import DataManagementTable from "../../src/components/data-management/DataManagementTable";
import { GridColDef } from "@mui/x-data-grid";

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

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/students/");
      if (response.ok) {
        const data = await response.json();
        // API 응답이 {"students": [...]} 형태이므로 data.students로 접근
        const studentsData = data.students || data;
        setStudents(Array.isArray(studentsData) ? studentsData : []);
      } else {
        setStudents([]);
      }
    } catch (error) {
      console.error('학생 데이터 로드 실패:', error);
      setStudents([]);
    } finally {
      setIsLoading(false);
    }
  };

  // DataGrid 컬럼 정의
  const studentColumns: GridColDef[] = [
    { field: "name", headerName: "이름", width: 170, editable: true },
    { field: "email", headerName: "이메일", width: 240, editable: true },
    { field: "phone", headerName: "전화번호", width: 180, editable: true },
    { field: "grade", headerName: "학년", width: 100, editable: true },
    { field: "tuition_fee", headerName: "수강료", width: 120, editable: true, type: "number" },
    { field: "tuition_due_date", headerName: "납부일", width: 140, editable: true },
    { field: "is_active", headerName: "상태", width: 110, editable: true, type: "singleSelect", valueOptions: ["활성", "비활성"] },
    { field: "created_at", headerName: "등록일", width: 140, editable: false }
  ];

  // CRUD 함수
  const handleRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      // 변경사항을 pendingChanges에 추가 (즉시 저장하지 않음)
      const change = {
        id: newRow.id,
        oldData: oldRow,
        newData: { ...newRow, is_active: newRow.is_active === "활성" },
        timestamp: Date.now()
      };
      
      // 중복된 변경사항이 있으면 제거하고 새로 추가
      setPendingChanges(prev => {
        const filtered = prev.filter(change => change.id !== newRow.id);
        return [...filtered, change];
      });
      
      // 로컬 상태 업데이트 (즉시 UI 반영)
      setStudents(prev => 
        prev.map(student => 
          student.id === newRow.id 
            ? { ...newRow, is_active: newRow.is_active === "활성" }
            : student
        )
      );
      
      return newRow;
    } catch (e) {
      console.error('업데이트 오류:', e);
      return oldRow;
    }
  };

  const handleAddRow = async () => {
    const newStudent = {
      name: "새 학생",
      email: `student${Date.now()}@example.com`,
      phone: "",
      grade: "1학년",
      tuition_fee: 0,
      tuition_due_date: "",
      is_active: true,
    };
    
    try {
      const response = await fetch("http://localhost:8000/api/v1/students/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newStudent),
      });
      
      if (response.ok) {
        await fetchStudents();
      } else {
        throw new Error("추가 실패");
      }
    } catch (error) {
      console.error('추가 오류:', error);
      alert('새 학생 추가 중 오류가 발생했습니다.');
    }
  };

  const handleDeleteRow = async (id: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/students/${id}`, { 
        method: "DELETE" 
      });
      
      if (response.ok) {
        await fetchStudents();
      } else {
        throw new Error("삭제 실패");
      }
    } catch (error) {
      console.error('삭제 오류:', error);
      alert('삭제 중 오류가 발생했습니다.');
    }
  };

  const handleSaveAll = async () => {
    if (pendingChanges.length === 0) return;
    
    try {
      // 모든 pending changes를 서버에 저장
      for (const change of pendingChanges) {
        const response = await fetch(`http://localhost:8000/api/v1/students/${change.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(change.newData),
        });
        
        if (!response.ok) {
          throw new Error(`학생 ID ${change.id} 업데이트 실패`);
        }
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
    />
  );
} 
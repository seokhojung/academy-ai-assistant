'use client';

import React, { useState, useEffect } from "react";
import DataManagementTable from "../../src/components/data-management/DataManagementTable";
import { GridColDef } from "@mui/x-data-grid";

interface Teacher {
  id: number;
  name: string;
  email: string;
  phone: string;
  subject: string;
  experience_years: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function TeachersPage() {
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTeachers();
  }, []);

  const fetchTeachers = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/teachers/");
      if (response.ok) {
        const data = await response.json();
        // API 응답이 {"teachers": [...]} 형태이므로 data.teachers로 접근
        const teachersData = data.teachers || data;
        setTeachers(Array.isArray(teachersData) ? teachersData : []);
      } else {
        setTeachers([]);
      }
    } catch (error) {
      console.error('강사 데이터 로드 실패:', error);
      setTeachers([]);
    } finally {
      setIsLoading(false);
    }
  };

  // DataGrid 컬럼 정의
  const teacherColumns: GridColDef[] = [
    { field: "name", headerName: "이름", width: 170, editable: true },
    { field: "email", headerName: "이메일", width: 240, editable: true },
    { field: "phone", headerName: "전화번호", width: 180, editable: true },
    { field: "subject", headerName: "담당 과목", width: 140, editable: true },
    { field: "experience_years", headerName: "경력(년)", width: 120, editable: true, type: "number" },
    { field: "is_active", headerName: "상태", width: 110, editable: true, type: "singleSelect", valueOptions: ["활성", "비활성"] },
    { field: "created_at", headerName: "등록일", width: 140, editable: false }
  ];

  // CRUD 함수
  const handleRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      const updateData = { ...newRow, is_active: newRow.is_active === "활성" };
      const response = await fetch(`http://localhost:8000/api/v1/teachers/${newRow.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updateData),
      });
      if (response.ok) {
        fetchTeachers();
        return newRow;
      } else {
        throw new Error("업데이트 실패");
      }
    } catch (e) {
      return oldRow;
    }
  };

  const handleAddRow = async () => {
    const newTeacher = {
      name: "새 강사",
      email: `teacher${Date.now()}@example.com`,
      phone: "",
      subject: "",
      experience_years: 0,
      is_active: true,
    };
    await fetch("http://localhost:8000/api/v1/teachers/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newTeacher),
    });
    fetchTeachers();
  };

  const handleDeleteRow = async (id: number) => {
    await fetch(`http://localhost:8000/api/v1/teachers/${id}`, { method: "DELETE" });
    fetchTeachers();
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
    />
  );
} 
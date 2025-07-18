'use client';

import React, { useState, useEffect } from "react";
import DataManagementTable from "../../src/components/data-management/DataManagementTable";
import { GridColDef } from "@mui/x-data-grid";
import { School } from "@mui/icons-material";

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

  useEffect(() => {
    fetchLectures();
  }, []);

  const fetchLectures = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/lectures/");
      if (response.ok) {
        const data = await response.json();
        const lecturesData = data.lectures || data;
        setLectures(Array.isArray(lecturesData) ? lecturesData : []);
      } else {
        setLectures([]);
      }
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

  // CRUD 함수
  const handleRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      const updateData = { ...newRow, is_active: newRow.is_active === "활성" };
      const response = await fetch(`http://localhost:8000/api/v1/lectures/${newRow.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updateData),
      });
      if (response.ok) {
        fetchLectures();
        return newRow;
      } else {
        throw new Error("업데이트 실패");
      }
    } catch (e) {
      return oldRow;
    }
  };

  const handleAddRow = async () => {
    const newLecture = {
      title: "새 강의",
      subject: "",
      grade: "",
      max_students: 20,
      current_students: 0,
      tuition_fee: 0,
      schedule: "",
      classroom: "",
      is_active: true,
      description: ""
    };
    await fetch("http://localhost:8000/api/v1/lectures/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newLecture),
    });
    fetchLectures();
  };

  const handleDeleteRow = async (id: number) => {
    await fetch(`http://localhost:8000/api/v1/lectures/${id}`, { method: "DELETE" });
    fetchLectures();
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
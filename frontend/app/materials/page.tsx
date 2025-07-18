'use client';

import React, { useState, useEffect } from "react";
import DataManagementTable from "../../src/components/data-management/DataManagementTable";
import { GridColDef } from "@mui/x-data-grid";

interface Material {
  id: number;
  name: string;  // title -> name으로 변경
  subject: string;
  grade: string;
  publisher: string;
  price: number;
  quantity: number;  // stock_quantity -> quantity로 변경
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function MaterialsPage() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchMaterials();
  }, []);

  const fetchMaterials = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/materials/");
      if (response.ok) {
        const data = await response.json();
        // API 응답이 {"materials": [...]} 형태이므로 data.materials로 접근
        const materialsData = data.materials || data;
        setMaterials(Array.isArray(materialsData) ? materialsData : []);
      } else {
        setMaterials([]);
      }
    } catch (error) {
      console.error('교재 데이터 로드 실패:', error);
      setMaterials([]);
    } finally {
      setIsLoading(false);
    }
  };

  // DataGrid 컬럼 정의
  const materialColumns: GridColDef[] = [
    { field: "name", headerName: "제목", width: 180, editable: true },  // title -> name으로 변경
    { field: "subject", headerName: "과목", width: 120, editable: true },
    { field: "grade", headerName: "학년", width: 100, editable: true },
    { field: "publisher", headerName: "출판사", width: 140, editable: true },
    { field: "price", headerName: "가격", width: 110, editable: true, type: "number" },
    { field: "quantity", headerName: "재고", width: 100, editable: true, type: "number" },  // stock_quantity -> quantity로 변경
    { field: "is_active", headerName: "상태", width: 110, editable: true, type: "singleSelect", valueOptions: ["활성", "비활성"] },
    { field: "created_at", headerName: "등록일", width: 140, editable: false }
  ];

  // CRUD 함수
  const handleRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      const updateData = { ...newRow, is_active: newRow.is_active === "활성" };
      const response = await fetch(`http://localhost:8000/api/v1/materials/${newRow.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updateData),
      });
      if (response.ok) {
        fetchMaterials();
        return newRow;
      } else {
        throw new Error("업데이트 실패");
      }
    } catch (e) {
      return oldRow;
    }
  };

  const handleAddRow = async () => {
    const newMaterial = {
      name: "새 교재",  // title -> name으로 변경
      subject: "",
      grade: "",
      publisher: "",
      price: 0,
      quantity: 0,  // stock_quantity -> quantity로 변경
      is_active: true,
    };
    await fetch("http://localhost:8000/api/v1/materials/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newMaterial),
    });
    fetchMaterials();
  };

  const handleDeleteRow = async (id: number) => {
    await fetch(`http://localhost:8000/api/v1/materials/${id}`, { method: "DELETE" });
    fetchMaterials();
  };

  // 통계 정보 계산
  const total = Array.isArray(materials) ? materials.length : 0;
  const active = Array.isArray(materials) ? materials.filter(m => m.is_active).length : 0;
  const inactive = Array.isArray(materials) ? materials.filter(m => !m.is_active).length : 0;
  const recentRegistration = Array.isArray(materials) && materials.length > 0 ? materials[0].name : undefined;  // title -> name으로 변경

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">로딩 중...</div>;
  }

  return (
    <DataManagementTable
      entityType="materials"
      title="교재 관리"
      description="교재 정보를 효율적으로 관리하세요!"
      columns={materialColumns}
      data={Array.isArray(materials) ? materials.map(m => ({ ...m, is_active: m.is_active ? "활성" : "비활성" })) : []}
      onRowUpdate={handleRowUpdate}
      onAddRow={handleAddRow}
      onDeleteRow={handleDeleteRow}
      summaryStats={{ total, active, inactive, recentRegistration }}
    />
  );
} 
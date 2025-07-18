'use client';

import React, { useState, useEffect } from "react";
import DataManagementTable from "../../src/components/data-management/DataManagementTable";
import { GridColDef } from "@mui/x-data-grid";
import { useHistoryManager } from "../../src/hooks/useHistoryManager";
import { EditEntityCommand, AddEntityCommand, DeleteEntityCommand } from "../../src/commands";
import { apiClient } from "../../src/lib/api-client";

interface Material {
  id: number;
  name: string;
  subject: string;
  grade: string;
  description: string | null;
  price: number;
  publisher: string | null;
  author: string | null;
  isbn: string | null;
  quantity: number;
  min_quantity: number;
  publication_date: string | null;
  edition: string | null;
  expiry_date: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function MaterialsPage() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // 히스토리 관리자 사용
  const { executeCommand } = useHistoryManager();

  useEffect(() => {
    fetchMaterials();
  }, []);

  const fetchMaterials = async () => {
    setIsLoading(true);
    try {
      console.log('[fetchMaterials] 교재 데이터 로드 시작');
      const data = await apiClient.getEntities('materials');
      console.log('[fetchMaterials] 받은 데이터:', data);
      console.log('[fetchMaterials] 데이터 타입:', typeof data);
      console.log('[fetchMaterials] 배열 여부:', Array.isArray(data));
      
      // apiClient.getEntities가 이미 올바른 배열을 반환함
      const materialsData = Array.isArray(data) ? data : [];
      console.log('[fetchMaterials] 설정할 데이터:', materialsData);
      setMaterials(materialsData);
    } catch (error) {
      console.error('[fetchMaterials] 교재 데이터 로드 실패:', error);
      setMaterials([]);
    } finally {
      setIsLoading(false);
      console.log('[fetchMaterials] 로딩 완료');
    }
  };

  // DataGrid 컬럼 정의
  const materialColumns: GridColDef[] = [
    { field: "name", headerName: "교재명", width: 150, editable: true },
    { field: "subject", headerName: "과목", width: 100, editable: true },
    { field: "grade", headerName: "학년", width: 80, editable: true },
    { field: "description", headerName: "설명", width: 150, editable: true },
    { field: "publisher", headerName: "출판사", width: 120, editable: true },
    { field: "author", headerName: "저자", width: 120, editable: true },
    { field: "isbn", headerName: "ISBN", width: 120, editable: true },
    { field: "price", headerName: "가격", width: 100, editable: true, type: "number" },
    { field: "quantity", headerName: "재고", width: 80, editable: true, type: "number" },
    { field: "min_quantity", headerName: "최소재고", width: 100, editable: true, type: "number" },
    { field: "edition", headerName: "판본", width: 80, editable: true },
    { field: "is_active", headerName: "상태", width: 100, editable: true, type: "singleSelect", valueOptions: ["활성", "비활성"] },
    { field: "created_at", headerName: "등록일", width: 120, editable: false }
  ];

  // CRUD 함수 - Command Pattern 기반
  const handleRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      // Command Pattern을 사용하여 편집 히스토리 관리
      const editCommand = new EditEntityCommand(
        'materials',
        newRow.id,
        oldRow,
        newRow, // EditEntityCommand에서 데이터 검증 및 변환 처리
        apiClient,
        (data) => {
          // 로컬 상태 업데이트
          setMaterials(prev => 
            prev.map(material => 
              material.id === newRow.id ? data : material
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
    const newMaterial = {
      name: "새 교재",
      subject: "수학",
      grade: "1학년",
      description: null,
      publisher: null,
      author: null,
      isbn: null,
      price: 0,
      quantity: 0,
      min_quantity: 5,
      publication_date: null,
      edition: null,
      expiry_date: null,
      is_active: true,
    };
    
    try {
      // Command Pattern을 사용하여 추가 히스토리 관리
      const addCommand = new AddEntityCommand(
        'materials',
        newMaterial,
        apiClient,
        (data) => {
          // 로컬 상태에 추가 (최신순으로 맨 위에)
          setMaterials(prev => [data, ...prev]);
        },
        (id) => {
          // 로컬 상태에서 제거
          setMaterials(prev => prev.filter(material => material.id !== id));
        }
      );
      
      await executeCommand(addCommand);
    } catch (error) {
      console.error('추가 오류:', error);
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
      alert(`새 교재 추가 중 오류가 발생했습니다: ${errorMessage}`);
    }
  };

  const handleDeleteRow = async (id: number) => {
    try {
      // 삭제할 교재 데이터 찾기
      const materialToDelete = materials.find(material => material.id === id);
      if (!materialToDelete) {
        throw new Error("삭제할 교재를 찾을 수 없습니다.");
      }

      // Command Pattern을 사용하여 삭제 히스토리 관리
      const deleteCommand = new DeleteEntityCommand(
        'materials',
        id,
        materialToDelete,
        apiClient,
        (id) => {
          // 로컬 상태에서 제거
          setMaterials(prev => prev.filter(material => material.id !== id));
        },
        (data) => {
          // 로컬 상태에 추가 (복구 시)
          setMaterials(prev => [data, ...prev]);
        }
      );
      
      await executeCommand(deleteCommand);
    } catch (error) {
      console.error('삭제 오류:', error);
      alert('삭제 중 오류가 발생했습니다.');
    }
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
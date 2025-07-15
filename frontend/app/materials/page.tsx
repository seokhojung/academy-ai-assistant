'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import AIChatBox from '../../components/ai-chat-box';
import ExcelPreviewTable from '../../components/excel-preview-table';
import { GridColDef } from '@mui/x-data-grid';

interface Material {
  id: number;
  title: string;
  subject: string;
  grade: string;
  publisher: string;
  price: number;
  stock_quantity: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function MaterialsPage() {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    grade: '',
    publisher: '',
    price: 0,
    stock_quantity: 0
  });

  useEffect(() => {
    fetchMaterials();
  }, []);

  const fetchMaterials = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/materials/');
      if (response.ok) {
        const data = await response.json();
        setMaterials(data);
      }
    } catch (error) {
      console.error('교재 목록 조회 실패:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/v1/materials/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        setIsDialogOpen(false);
        setFormData({ title: '', subject: '', grade: '', publisher: '', price: 0, stock_quantity: 0 });
        fetchMaterials();
      }
    } catch (error) {
      console.error('교재 등록 실패:', error);
    }
  };

  // 교재 DataGrid 컬럼 정의
  const materialColumns: GridColDef[] = [
    { field: 'title', headerName: '제목', width: 180, minWidth: 140, headerAlign: 'left', align: 'center', editable: true, type: 'string' },
    { field: 'subject', headerName: '과목', width: 120, minWidth: 90, headerAlign: 'left', align: 'center', editable: true, type: 'string' },
    { field: 'grade', headerName: '학년', width: 100, minWidth: 80, headerAlign: 'left', align: 'center', editable: true, type: 'string' },
    { field: 'publisher', headerName: '출판사', width: 140, minWidth: 100, headerAlign: 'left', align: 'center', editable: true, type: 'string' },
    { field: 'price', headerName: '가격', width: 110, minWidth: 90, headerAlign: 'left', align: 'center', editable: true, type: 'number' },
    { field: 'stock_quantity', headerName: '재고', width: 100, minWidth: 80, headerAlign: 'left', align: 'center', editable: true, type: 'number' },
    { field: 'is_active', headerName: '상태', width: 110, minWidth: 90, headerAlign: 'left', align: 'center', editable: true, type: 'singleSelect', valueOptions: ['활성', '비활성'] },
    { field: 'created_at', headerName: '등록일', width: 140, minWidth: 110, headerAlign: 'left', align: 'center', editable: false, type: 'string' }
  ];

  // 교재 rows 변환
  const materialRows = materials.map((m) => ({
    id: m.id,
    title: m.title,
    subject: m.subject,
    grade: m.grade,
    publisher: m.publisher,
    price: m.price,
    stock_quantity: m.stock_quantity,
    is_active: m.is_active ? '활성' : '비활성',
    created_at: typeof m.created_at === 'string' ? m.created_at.slice(0, 10) : '',
  }));

  // DataGrid용 CRUD 핸들러(간단 버전)
  const handleMaterialRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      const updateData = {
        title: newRow.title,
        subject: newRow.subject,
        grade: newRow.grade,
        publisher: newRow.publisher,
        price: Number(newRow.price),
        stock_quantity: Number(newRow.stock_quantity),
        is_active: newRow.is_active === '활성',
      };
      const response = await fetch(`http://localhost:8000/api/v1/materials/${newRow.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData),
      });
      if (response.ok) {
        fetchMaterials();
        return newRow;
      } else {
        throw new Error('업데이트 실패');
      }
    } catch (e) {
      return oldRow;
    }
  };
  const handleMaterialAddRow = async () => {
    const newMaterial = {
      title: '새 교재',
      subject: '',
      grade: '',
      publisher: '',
      price: 0,
      stock_quantity: 0,
      is_active: true,
    };
    await fetch('http://localhost:8000/api/v1/materials/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newMaterial),
    });
    fetchMaterials();
  };
  const handleMaterialDeleteRow = async (id: number) => {
    await fetch(`http://localhost:8000/api/v1/materials/${id}`, { method: 'DELETE' });
    fetchMaterials();
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-64">로딩 중...</div>;
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">교재 관리</h1>
      {/* 엑셀 미리보기(DataGrid) */}
      <ExcelPreviewTable
        title="교재 엑셀 미리보기"
        rows={materialRows}
        columns={materialColumns}
        onRowUpdate={handleMaterialRowUpdate}
        onAddRow={handleMaterialAddRow}
        onDeleteRow={handleMaterialDeleteRow}
      />
      {/* 기존 카드 리스트 UI */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {materials.map((material) => (
          <Card key={material.id}>
            <CardHeader>
              <CardTitle className="flex justify-between items-center">
                {material.title}
                <span className={`px-2 py-1 text-xs rounded ${
                  material.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {material.is_active ? '활성' : '비활성'}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p><strong>과목:</strong> {material.subject}</p>
                <p><strong>학년:</strong> {material.grade}</p>
                <p><strong>출판사:</strong> {material.publisher}</p>
                <p><strong>가격:</strong> {material.price.toLocaleString()}원</p>
                <p><strong>재고:</strong> {material.stock_quantity}권</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      <AIChatBox />
    </div>
  );
} 
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { TableRowSkeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/use-toast';
import AIChatBox from '../../components/ai-chat-box';
import ExcelPreviewTable from '../../components/excel-preview-table';
import { GridColDef } from '@mui/x-data-grid';

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
  const { toast } = useToast();
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    experience_years: 0
  });

  useEffect(() => {
    fetchTeachers();
  }, []);

  const fetchTeachers = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/teachers/');
      if (response.ok) {
        const data = await response.json();
        setTeachers(data);
      }
    } catch (error) {
      console.error('강사 목록 조회 실패:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/v1/teachers/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        setIsDialogOpen(false);
        setFormData({ name: '', email: '', phone: '', subject: '', experience_years: 0 });
        fetchTeachers();
        toast({
          title: "강사 등록 완료",
          description: "새로운 강사가 성공적으로 등록되었습니다.",
          variant: "success",
        });
      }
    } catch (error) {
      console.error('강사 등록 실패:', error);
    }
  };

  // 강사 DataGrid 컬럼 정의
  const teacherColumns: GridColDef[] = [
    { field: 'name', headerName: '이름', width: 170, minWidth: 140, headerAlign: 'left', align: 'center', editable: true, type: 'string' },
    { field: 'email', headerName: '이메일', width: 240, minWidth: 180, headerAlign: 'left', align: 'center', editable: true, type: 'string' },
    { field: 'phone', headerName: '전화번호', width: 180, minWidth: 140, headerAlign: 'left', align: 'center', editable: true, type: 'string' },
    { field: 'subject', headerName: '담당 과목', width: 140, minWidth: 110, headerAlign: 'left', align: 'center', editable: true, type: 'string' },
    { field: 'experience_years', headerName: '경력(년)', width: 120, minWidth: 90, headerAlign: 'left', align: 'center', editable: true, type: 'number' },
    { field: 'is_active', headerName: '상태', width: 110, minWidth: 90, headerAlign: 'left', align: 'center', editable: true, type: 'singleSelect', valueOptions: ['활성', '비활성'] },
    { field: 'created_at', headerName: '등록일', width: 140, minWidth: 110, headerAlign: 'left', align: 'center', editable: false, type: 'string' }
  ];

  // 강사 rows 변환
  const teacherRows = teachers.map((t) => ({
    id: t.id,
    name: t.name,
    email: t.email,
    phone: t.phone,
    subject: t.subject,
    experience_years: t.experience_years,
    is_active: t.is_active ? '활성' : '비활성',
    created_at: typeof t.created_at === 'string' ? t.created_at.slice(0, 10) : '',
  }));

  // DataGrid용 CRUD 핸들러(간단 버전)
  const handleTeacherRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      const updateData = {
        name: newRow.name,
        email: newRow.email,
        phone: newRow.phone,
        subject: newRow.subject,
        experience_years: Number(newRow.experience_years),
        is_active: newRow.is_active === '활성',
      };
      const response = await fetch(`http://localhost:8000/api/v1/teachers/${newRow.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData),
      });
      if (response.ok) {
        fetchTeachers();
        return newRow;
      } else {
        throw new Error('업데이트 실패');
      }
    } catch (e) {
      return oldRow;
    }
  };
  const handleTeacherAddRow = async () => {
    const newTeacher = {
      name: '새 강사',
      email: `teacher${Date.now()}@example.com`,
      phone: '',
      subject: '',
      experience_years: 0,
      is_active: true,
    };
    await fetch('http://localhost:8000/api/v1/teachers/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newTeacher),
    });
    fetchTeachers();
  };
  const handleTeacherDeleteRow = async (id: number) => {
    await fetch(`http://localhost:8000/api/v1/teachers/${id}`, { method: 'DELETE' });
    fetchTeachers();
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">강사 관리</h1>
          <Button disabled>새 강사 등록</Button>
        </div>
        <TableRowSkeleton rows={6} />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">강사 관리</h1>
      {/* 엑셀 미리보기(DataGrid) */}
      <ExcelPreviewTable
        title="강사 엑셀 미리보기"
        rows={teacherRows}
        columns={teacherColumns}
        onRowUpdate={handleTeacherRowUpdate}
        onAddRow={handleTeacherAddRow}
        onDeleteRow={handleTeacherDeleteRow}
      />
      {/* 기존 카드 리스트 UI */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {teachers.map((teacher) => (
          <Card key={teacher.id}>
            <CardHeader>
              <CardTitle className="flex justify-between items-center">
                {teacher.name}
                <span className={`px-2 py-1 text-xs rounded ${
                  teacher.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {teacher.is_active ? '활성' : '비활성'}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p><strong>이메일:</strong> {teacher.email}</p>
                <p><strong>전화번호:</strong> {teacher.phone}</p>
                <p><strong>담당 과목:</strong> {teacher.subject}</p>
                <p><strong>경력:</strong> {teacher.experience_years}년</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      <AIChatBox />
    </div>
  );
} 
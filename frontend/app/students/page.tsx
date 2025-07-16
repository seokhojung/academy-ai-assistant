'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
import { TextField } from '@mui/material';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { TableRowSkeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '../../lib/api-client';
import AIChatBox from '../../components/ai-chat-box';
import { HotTable } from '@handsontable/react';
import Handsontable from 'handsontable';
import 'handsontable/dist/handsontable.full.min.css';
import { DataGrid, GridColDef, GridRowsProp, GridToolbar, useGridApiRef, GridSortModel } from '@mui/x-data-grid';
import { Box, Paper, Button as MuiButton, IconButton, Tooltip, Menu, MenuItem, ListItemIcon, ListItemText, Chip, Divider, Checkbox } from '@mui/material';
import { Undo, Redo, Save, Cancel, Add, Delete, Edit, MoreVert, ViewColumn, ViewColumnOutlined, Pause, ArrowDownward, FilterList, VisibilityOff, DragIndicator } from '@mui/icons-material';
import SchoolRounded from '@mui/icons-material/SchoolRounded';
import PeopleAltRounded from '@mui/icons-material/PeopleAltRounded';
import PersonAddAlt1Rounded from '@mui/icons-material/PersonAddAlt1Rounded';
import PersonOffRounded from '@mui/icons-material/PersonOffRounded';
import ArrowUpward from '@mui/icons-material/ArrowUpward';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { GlobalStyles } from '@mui/material';

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

interface EditHistory {
  id: number;
  oldData: any;
  newData: any;
  timestamp: number;
  field?: string;
}

export default function StudentsPage() {
  const { toast } = useToast();
  const [students, setStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    grade: '',
    tuition_fee: 0,
    tuition_due_date: ''
  });
  const [search, setSearch] = useState('');
  const [filteredStudents, setFilteredStudents] = useState<Student[]>([]);
  
  // Undo/Redo 상태 관리
  const [editHistory, setEditHistory] = useState<EditHistory[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isUndoRedoEnabled, setIsUndoRedoEnabled] = useState(false);
  
  // 동적 컬럼 관리
  const [columns, setColumns] = useState<GridColDef[]>([
    { field: 'name', headerName: '이름', width: 170, minWidth: 140, headerAlign: 'left', align: 'center', editable: true, type: 'string', cellClassName: 'text-center' },
    { 
      field: 'email', 
      headerName: '이메일', 
      width: 320, 
      minWidth: 280, 
      headerAlign: 'left', 
      align: 'center', 
      editable: true, 
      type: 'string', 
      cellClassName: 'text-center',
      renderCell: (params) => (
        <Tooltip title={params.value} placement="top-start">
          <span style={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis', 
            whiteSpace: 'nowrap',
            width: '100%',
            display: 'block'
          }}>
            {params.value}
          </span>
        </Tooltip>
      )
    },
    { field: 'phone', headerName: '전화번호', width: 190, minWidth: 160, headerAlign: 'left', align: 'center', editable: true, type: 'string', cellClassName: 'text-center' },
    { field: 'grade', headerName: '학년', width: 130, minWidth: 110, headerAlign: 'left', align: 'center', editable: true, type: 'string', cellClassName: 'text-center' },
    { field: 'tuition_fee', headerName: '수강료', width: 150, minWidth: 120, headerAlign: 'left', align: 'center', editable: true, type: 'number', cellClassName: 'text-center' },
    { field: 'tuition_due_date', headerName: '납부일', width: 160, minWidth: 130, headerAlign: 'left', align: 'center', editable: true, type: 'date', cellClassName: 'text-center' },
    { field: 'is_active', headerName: '상태', width: 130, minWidth: 110, headerAlign: 'left', align: 'center', editable: true, type: 'singleSelect', valueOptions: ['활성', '비활성'], cellClassName: 'text-center' },
    { field: 'created_at', headerName: '등록일', width: 160, minWidth: 130, headerAlign: 'left', align: 'center', editable: false, type: 'string', cellClassName: 'text-center' }
  ]);

  // 컬럼 헤더 편집 상태
  const [editingHeader, setEditingHeader] = useState<string | null>(null);
  const [headerEditValue, setHeaderEditValue] = useState('');
  
  // 컬럼 순서 관리
  const [columnOrder, setColumnOrder] = useState<string[]>([]);
  
  // 컬럼 순서 초기화
  useEffect(() => {
    if (columns.length > 0) {
      const columnFields = columns.map(col => col.field);
      if (columnOrder.length === 0 || JSON.stringify(columnOrder) !== JSON.stringify(columnFields)) {
        console.log('Initializing column order:', columnFields);
        setColumnOrder(columnFields);
      }
    }
  }, [columns, columnOrder]);
  
  // 컬럼 순서에 따라 정렬된 컬럼 배열 생성
  const orderedColumns = useMemo(() => {
    console.log('Creating ordered columns:', { columnOrder, columnsLength: columns.length });
    
    if (columnOrder.length === 0 || columnOrder.length !== columns.length) {
      console.log('Using original columns order');
      return columns;
    }
    
    const columnMap = new Map(columns.map(col => [col.field, col]));
    const ordered = columnOrder
      .map(field => columnMap.get(field))
      .filter(Boolean) as GridColDef[];
    
    console.log('Ordered columns result:', ordered.map(col => col.field));
    return ordered;
  }, [columns, columnOrder]);
  
  // 드래그 앤 드롭 상태
  const [draggedColumn, setDraggedColumn] = useState<string | null>(null);
  
  // 드래그 시작
  const handleDragStart = (e: React.DragEvent, field: string) => {
    setDraggedColumn(field);
    e.dataTransfer.effectAllowed = 'move';
  };
  
  // 드래그 오버
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };
  
  // 드롭
  const handleDrop = (e: React.DragEvent, targetField: string) => {
    e.preventDefault();
    console.log('Drop event:', { draggedColumn, targetField });
    
    if (draggedColumn && draggedColumn !== targetField) {
      const newOrder = [...columnOrder];
      const draggedIndex = newOrder.indexOf(draggedColumn);
      const targetIndex = newOrder.indexOf(targetField);
      
      console.log('Column order before:', newOrder);
      console.log('Dragged index:', draggedIndex, 'Target index:', targetIndex);
      
      // 드래그된 컬럼 제거
      newOrder.splice(draggedIndex, 1);
      // 타겟 위치에 삽입
      newOrder.splice(targetIndex, 0, draggedColumn);
      
      console.log('Column order after:', newOrder);
      
      setColumnOrder(newOrder);
      
      toast({
        title: "컬럼 순서 변경 완료",
        description: "컬럼 순서가 변경되었습니다.",
        variant: "success",
      });
    }
    setDraggedColumn(null);
  };

  // 컬럼 헤더 편집 시작
  const handleHeaderEditStart = (field: string, currentHeader: string) => {
    setEditingHeader(field);
    setHeaderEditValue(currentHeader);
  };

  // 컬럼 헤더 편집 완료
  const handleHeaderEditComplete = (field: string) => {
    if (editingHeader === field && headerEditValue.trim()) {
      setColumns(prev => prev.map(col => 
        col.field === field 
          ? { ...col, headerName: headerEditValue.trim() }
          : col
      ));
      
      // 컬럼 메타데이터를 로컬 스토리지에 업데이트
      try {
        const savedColumns = localStorage.getItem('studentTableColumns');
        if (savedColumns) {
          const columnsData = JSON.parse(savedColumns);
          const updatedColumns = columnsData.map((col: any) => 
            col.field === field 
              ? { ...col, headerName: headerEditValue.trim() }
              : col
          );
          localStorage.setItem('studentTableColumns', JSON.stringify(updatedColumns));
        }
      } catch (error) {
        console.error('컬럼 메타데이터 업데이트 실패:', error);
      }
      
      toast({
        title: "헤더 수정 완료",
        description: `컬럼 헤더가 "${headerEditValue.trim()}"로 변경되었습니다. (새로고침 후에도 유지됩니다)`,
        variant: "success",
      });
    }
    setEditingHeader(null);
    setHeaderEditValue('');
  };

  // 컬럼 헤더 편집 취소
  const handleHeaderEditCancel = () => {
    setEditingHeader(null);
    setHeaderEditValue('');
  };

  // 새 컬럼 추가
  const handleAddColumn = () => {
    const newField = `custom_${Date.now()}`;
    const newColumn: GridColDef = {
      field: newField,
      headerName: '새 컬럼',
      width: 150,
      minWidth: 120,
      headerAlign: 'left',
      align: 'center',
      editable: true,
      type: 'string',
      cellClassName: 'text-center'
    };
    
    setColumns(prev => [...prev, newColumn]); // 항상 맨 마지막에 추가
    
    // 컬럼 메타데이터를 로컬 스토리지에 저장
    try {
      const savedColumns = localStorage.getItem('studentTableColumns');
      const columnsData = savedColumns ? JSON.parse(savedColumns) : [];
      columnsData.push({
        field: newField,
        headerName: '새 컬럼',
        type: 'string'
      });
      localStorage.setItem('studentTableColumns', JSON.stringify(columnsData));
    } catch (error) {
      console.error('컬럼 메타데이터 저장 실패:', error);
    }
    
    toast({
      title: "컬럼 추가 완료",
      description: "새로운 컬럼이 추가되었습니다. (새로고침 후에도 유지됩니다)",
      variant: "success",
    });
  };

  // 컬럼 삭제
  const handleDeleteColumn = (field: string) => {
    if (field === 'id' || field === 'actions' || field === 'created_at') {
      toast({
        title: "삭제 불가",
        description: "이 컬럼은 삭제할 수 없습니다.",
        variant: "destructive",
      });
      return;
    }
    
    setColumns(prev => prev.filter(col => col.field !== field));
    
    // 컬럼 메타데이터를 로컬 스토리지에서 제거
    try {
      const savedColumns = localStorage.getItem('studentTableColumns');
      if (savedColumns) {
        const columnsData = JSON.parse(savedColumns);
        const filteredColumns = columnsData.filter((col: any) => col.field !== field);
        localStorage.setItem('studentTableColumns', JSON.stringify(filteredColumns));
      }
    } catch (error) {
      console.error('컬럼 메타데이터 삭제 실패:', error);
    }
    
    toast({
      title: "컬럼 삭제 완료",
      description: "컬럼이 삭제되었습니다. (새로고침 후에도 유지됩니다)",
      variant: "success",
    });
  };

  // 새 행 추가
  const handleAddRow = async () => {
    try {
      // 기본 데이터로 새 학생 생성
      const newStudentData = {
        name: '새 학생',
        email: `student${Date.now()}@example.com`,
        phone: '',
        grade: '',
        tuition_fee: 0.0,  // float로 전송
        tuition_due_date: null  // null은 백엔드에서 허용됨
      };
      
      console.log('새 학생 생성 데이터:', newStudentData);
      
      const response = await apiClient.createStudent(newStudentData);
      console.log('새 학생 생성 응답:', response);
      
      if (response.success) {
        toast({
          title: "행 추가 완료",
          description: "새로운 학생이 성공적으로 추가되었습니다.",
          variant: "success",
        });
        // 데이터 새로고침
        fetchStudents();
        // 히스토리 초기화
        clearHistory();
      } else {
        throw new Error(response.message || '학생 생성 실패');
      }
    } catch (error) {
      console.error('새 행 추가 실패:', error);
      toast({
        title: "행 추가 실패",
        description: "새로운 행을 추가하는데 실패했습니다.",
        variant: "destructive",
      });
    }
  };

  // 행 삭제 (선택된 행들)
  const handleDeleteSelectedRows = async (selectedIds: any[]) => {
    console.log('삭제할 선택된 행들:', selectedIds);
    
    // 배열이 아니거나 길이가 0인 경우
    if (!Array.isArray(selectedIds) || selectedIds.length === 0) {
      toast({
        title: "선택된 행 없음",
        description: "삭제할 행을 선택해주세요.",
        variant: "destructive",
      });
      return;
    }
    
    try {
      // 삭제 전 데이터 백업 (Undo/Redo용)
      const deletedRows = students.filter(s => selectedIds.includes(s.id));
      deletedRows.forEach(row => {
        addToHistory(row, null, 'hard_delete');
      });
      // 선택된 모든 행을 백엔드에서 하드 딜리트
      for (const id of selectedIds) {
        console.log('하드 딜리트 중인 ID:', id);
        await apiClient.deleteStudentHard(id);
      }
      toast({
        title: "학생 완전 삭제 완료",
        description: `${selectedIds.length}명의 학생이 완전히 삭제되었습니다.`,
        variant: "success",
      });
      
      // 데이터 새로고침
      fetchStudents();
      // 선택 상태 초기화
      setSelectedRows([]);
      // 히스토리 활성화 (clearHistory는 호출하지 않음)
    } catch (error) {
      console.error('선택된 행 하드 삭제 실패:', error);
      toast({
        title: "삭제 실패",
        description: "선택된 행을 완전히 삭제하는데 실패했습니다.",
        variant: "destructive",
      });
    }
  };

  // 컬럼 관리 메뉴 상태
  const [columnMenuAnchor, setColumnMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedColumn, setSelectedColumn] = useState<string | null>(null);
  
  // 행 선택 상태
  const [selectedRows, setSelectedRows] = useState<number[]>([]);

  // 컬럼 메뉴 열기
  const handleColumnMenuOpen = (event: React.MouseEvent<HTMLElement>, field: string) => {
    setColumnMenuAnchor(event.currentTarget);
    setSelectedColumn(field);
  };

  // 컬럼 메뉴 닫기
  const handleColumnMenuClose = () => {
    setColumnMenuAnchor(null);
    setSelectedColumn(null);
  };

  // 행 선택 변경
  const handleRowSelectionChange = (newSelection: any) => {
    console.log('행 선택 변경:', newSelection);
    // newSelection이 Set 객체인 경우 배열로 변환
    if (newSelection && typeof newSelection === 'object' && newSelection.ids) {
      setSelectedRows(Array.from(newSelection.ids));
    } else if (Array.isArray(newSelection)) {
      setSelectedRows(newSelection);
    } else {
      setSelectedRows([]);
    }
  };

  // 저장된 컬럼 메타데이터 로드
  useEffect(() => {
    try {
      const savedColumns = localStorage.getItem('studentTableColumns');
      if (savedColumns) {
        const columnsData = JSON.parse(savedColumns);
        if (Array.isArray(columnsData) && columnsData.length > 0) {
          // 기본 컬럼들 (actions 컬럼 제외)
          const baseColumns = columns.filter(col => col.field !== 'actions');
          
          // 저장된 커스텀 컬럼들을 GridColDef 형식으로 변환
          const customColumns: GridColDef[] = columnsData.map((col: any) => ({
            field: col.field,
            headerName: col.headerName || '새 컬럼',
            width: 150,
            minWidth: 120,
            editable: true,
            type: col.type || 'string'
          }));
          
          // actions 컬럼
          const actionsColumn = columns.find(col => col.field === 'actions');
          
          // 모든 컬럼 결합
          const newColumns = [...baseColumns, ...customColumns];
          if (actionsColumn) {
            newColumns.push(actionsColumn);
          }
          
          setColumns(newColumns);
        }
      }
    } catch (error) {
      console.error('저장된 컬럼 메타데이터 로드 실패:', error);
    }
  }, []);

  useEffect(() => {
    fetchStudents();
  }, []);

  useEffect(() => {
    if (!search) {
      setFilteredStudents(students);
    } else {
      setFilteredStudents(
        students.filter(s =>
          s.name.includes(search) ||
          s.email.includes(search) ||
          s.phone.includes(search) ||
          s.grade.includes(search) ||
          s.tuition_fee.toString().includes(search)
        )
      );
    }
  }, [search, students]);

  // 키보드 단축키 처리
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'z') {
        event.preventDefault();
        if (event.shiftKey) {
          handleRedo();
        } else {
          handleUndo();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []); // 의존성 배열을 비워서 무한 루프 방지

  const fetchStudents = async () => {
    try {
      const response = await apiClient.getStudents();
      if (response.success && response.data) {
        // 모든 학생(활성/비활성) 표시
        const studentsWithDate = (response.data as Student[]).map(student => ({
          ...student,
          tuition_due_date: student.tuition_due_date ? new Date(student.tuition_due_date) : null
        }));

        setStudents(studentsWithDate);
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      console.error('학생 목록 조회 실패:', error);
      toast({
        title: "데이터 로드 실패",
        description: "학생 목록을 불러오는데 실패했습니다.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // 편집 히스토리에 추가
  const addToHistory = useCallback((oldData: any, newData: any, field?: string) => {
    console.log('히스토리에 추가:', { oldData, newData, field });
    
    const historyItem: EditHistory = {
      id: oldData.id,
      oldData: { ...oldData },
      newData: { ...newData },
      timestamp: Date.now(),
      field
    };

    setEditHistory(prev => {
      // 현재 인덱스 이후의 히스토리 제거 (새로운 편집이 시작됨)
      const newHistory = prev.slice(0, historyIndex + 1);
      const updatedHistory = [...newHistory, historyItem];
      console.log('업데이트된 히스토리:', updatedHistory);
      return updatedHistory;
    });
    
    setHistoryIndex(prev => {
      const newIndex = prev + 1;
      console.log('새 히스토리 인덱스:', newIndex);
      return newIndex;
    });
    setIsUndoRedoEnabled(true);
  }, [historyIndex]);

  // Undo 기능
  const handleUndo = useCallback(async () => {
    console.log('Undo 실행:', { historyIndex, editHistoryLength: editHistory.length });
    
    if (historyIndex < 0) {
      console.log('Undo 불가: 히스토리 인덱스가 0보다 작음');
      return;
    }

    const historyItem = editHistory[historyIndex];
    if (!historyItem) {
      console.log('Undo 불가: 히스토리 아이템이 없음');
      return;
    }

    try {
      if (historyItem.field === 'hard_delete') {
        // 완전 삭제 Undo: 학생 복구(재등록)
        const { oldData } = historyItem;
        // id 중복 방지: 백엔드에서 id 지정 등록이 불가하면 새 id로 등록됨
        const { id, ...studentData } = oldData;
        const response = await apiClient.createStudent(studentData);
        if (response.success) {
          setHistoryIndex(prev => prev - 1);
          fetchStudents();
          toast({
            title: "삭제 취소 완료",
            description: `학생이 복구되었습니다. (id는 새로 부여될 수 있음)`,
            variant: "success",
          });
        } else {
          throw new Error(response.message);
        }
        return;
      }
      // 기존 Undo 로직 (수정 취소)
      console.log('Undo 실행 중:', historyItem);
      
      // 백엔드 API 형식으로 데이터 변환
      const oldDataForAPI = {
        name: historyItem.oldData.name,
        email: historyItem.oldData.email,
        phone: historyItem.oldData.phone,
        grade: historyItem.oldData.grade,
        tuition_fee: Number(historyItem.oldData.tuition_fee),
        tuition_due_date: historyItem.oldData.tuition_due_date || null,
        is_active: historyItem.oldData.is_active === '활성'
      };
      
      console.log('API로 보낼 데이터:', oldDataForAPI);
      
      // 백엔드에 원래 데이터로 되돌리기
      const response = await apiClient.updateStudent(historyItem.id, oldDataForAPI);
      
      if (response.success) {
        setHistoryIndex(prev => prev - 1);
        fetchStudents();
        toast({
          title: "실행 취소 완료",
          description: `${historyItem.field ? historyItem.field + ' 필드' : '학생 정보'}가 되돌려졌습니다.`,
          variant: "success",
        });
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      console.error('Undo 실패:', error);
      toast({
        title: "실행 취소 실패",
        description: "변경사항을 되돌리는데 실패했습니다.",
        variant: "destructive",
      });
    }
  }, [editHistory, historyIndex, fetchStudents, toast]);

  // Redo 기능
  const handleRedo = useCallback(async () => {
    console.log('Redo 실행:', { historyIndex, editHistoryLength: editHistory.length });
    
    if (historyIndex >= editHistory.length - 1) {
      console.log('Redo 불가: 히스토리 인덱스가 최대값에 도달');
      return;
    }

    const historyItem = editHistory[historyIndex + 1];
    if (!historyItem) {
      console.log('Redo 불가: 히스토리 아이템이 없음');
      return;
    }

    try {
      if (historyItem.field === 'hard_delete') {
        // 완전 삭제 Redo: 학생 다시 삭제
        const { oldData } = historyItem;
        const response = await apiClient.deleteStudentHard(oldData.id);
        if (response.success) {
          setHistoryIndex(prev => prev + 1);
          fetchStudents();
          toast({
            title: "삭제 다시 실행 완료",
            description: `학생이 다시 완전히 삭제되었습니다.`,
            variant: "success",
          });
        } else {
          throw new Error(response.message);
        }
        return;
      }
      // 기존 Redo 로직 (수정 다시 적용)
      console.log('Redo 실행 중:', historyItem);
      
      // 백엔드 API 형식으로 데이터 변환
      const newDataForAPI = {
        name: historyItem.newData.name,
        email: historyItem.newData.email,
        phone: historyItem.newData.phone,
        grade: historyItem.newData.grade,
        tuition_fee: Number(historyItem.newData.tuition_fee),
        tuition_due_date: historyItem.newData.tuition_due_date || null,
        is_active: historyItem.newData.is_active === '활성'
      };
      
      console.log('API로 보낼 데이터:', newDataForAPI);
      
      // 백엔드에 새로운 데이터로 다시 적용
      const response = await apiClient.updateStudent(historyItem.id, newDataForAPI);
      
      if (response.success) {
        setHistoryIndex(prev => prev + 1);
        fetchStudents();
        toast({
          title: "다시 실행 완료",
          description: `${historyItem.field ? historyItem.field + ' 필드' : '학생 정보'}가 다시 적용되었습니다.`,
          variant: "success",
        });
      } else {
        throw new Error(response.message);
      }
    } catch (error) {
      console.error('Redo 실패:', error);
      toast({
        title: "다시 실행 실패",
        description: "변경사항을 다시 적용하는데 실패했습니다.",
        variant: "destructive",
      });
    }
  }, [editHistory, historyIndex, fetchStudents, toast]);

  // 히스토리 초기화
  const clearHistory = useCallback(() => {
    setEditHistory([]);
    setHistoryIndex(-1);
    setIsUndoRedoEnabled(false);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 폼 데이터 검증
    if (!formData.name.trim()) {
      toast({
        title: "입력 오류",
        description: "학생 이름을 입력해주세요.",
        variant: "destructive",
      });
      return;
    }
    
    if (!formData.email.trim()) {
      toast({
        title: "입력 오류",
        description: "이메일을 입력해주세요.",
        variant: "destructive",
      });
      return;
    }
    
    try {
      // tuition_due_date 처리: 빈 문자열이면 null, 있으면 ISO 문자열로 변환
      let tuitionDueDate = null;
      if (formData.tuition_due_date && formData.tuition_due_date.trim()) {
        // 날짜 문자열을 ISO 형식으로 변환
        const date = new Date(formData.tuition_due_date);
        if (!isNaN(date.getTime())) {
          tuitionDueDate = date.toISOString();
        }
      }
      
      const submitData = {
        ...formData,
        tuition_fee: parseFloat(formData.tuition_fee.toString()) || 0.0,
        tuition_due_date: tuitionDueDate
      };
      
      console.log('학생 등록 데이터:', submitData);
      console.log('JSON 문자열:', JSON.stringify(submitData, null, 2));
      
      const response = await apiClient.createStudent(submitData);
      console.log('학생 등록 응답:', response);
      
      if (response.success) {
        setIsDialogOpen(false);
        setFormData({ name: '', email: '', phone: '', grade: '', tuition_fee: 0, tuition_due_date: '' });
        fetchStudents();
        clearHistory(); // 새 학생 등록 시 히스토리 초기화
        toast({
          title: "학생 등록 완료",
          description: "새로운 학생이 성공적으로 등록되었습니다.",
          variant: "success",
        });
      } else {
        throw new Error(response.message || '등록 실패');
      }
    } catch (error) {
      console.error('학생 등록 실패:', error);
      toast({
        title: "등록 실패",
        description: error instanceof Error ? error.message : "학생 등록에 실패했습니다.",
        variant: "destructive",
      });
    }
  };

  // DataGrid rows/columns 변환
  const rows: any[] = filteredStudents.map((s) => ({
    id: s.id,
    name: s.name,
    email: s.email,
    phone: s.phone,
    grade: s.grade,
    tuition_fee: s.tuition_fee,
    tuition_due_date: s.tuition_due_date
      ? (s.tuition_due_date instanceof Date
          ? s.tuition_due_date
          : new Date(s.tuition_due_date))
      : null,
    is_active: s.is_active ? '활성' : '비활성',
    created_at: typeof s.created_at === 'string' ? s.created_at.slice(0, 10) : '',
  }));

  // 편집 이벤트 핸들러
  const handleRowUpdate = async (newRow: any, oldRow: any) => {
    try {
      console.log('편집 시작:', { newRow, oldRow });
      
      // 편집 히스토리에 추가
      addToHistory(oldRow, newRow);
      
      // DataGrid의 데이터를 백엔드 API 형식으로 변환
      const updateData = {
        name: newRow.name,
        email: newRow.email,
        phone: newRow.phone,
        grade: newRow.grade,
        tuition_fee: Number(newRow.tuition_fee),
        tuition_due_date: newRow.tuition_due_date || null,
        is_active: newRow.is_active === '활성'
      };
      
      console.log('업데이트 데이터:', updateData);
      
      const response = await apiClient.updateStudent(newRow.id, updateData);
      console.log('API 응답:', response);
      
      if (response.success) {
        toast({ title: '저장 완료', description: '학생 정보가 업데이트되었습니다.', variant: 'success' });
        fetchStudents();
        return newRow;
      } else {
        throw new Error(response.message || '업데이트 실패');
      }
    } catch (e) {
      console.error('편집 실패:', e);
      toast({ title: '저장 실패', description: String(e), variant: 'destructive' });
      return oldRow;
    }
  };

  const handleRowDelete = async (id: number) => {
    try {
      await apiClient.deleteStudent(id);
      toast({ title: '삭제 완료', description: '학생이 비활성화되었습니다.', variant: 'success' });
      fetchStudents();
      clearHistory(); // 삭제 시 히스토리 초기화
    } catch (e) {
      toast({ title: '삭제 실패', description: String(e), variant: 'destructive' });
    }
  };

  const handleManualEdit = async (row: any) => {
    try {
      console.log('수동 편집 시작:', row);
      
      // DataGrid의 데이터를 백엔드 API 형식으로 변환
      const updateData = {
        name: row.name,
        email: row.email,
        phone: row.phone,
        grade: row.grade,
        tuition_fee: Number(row.tuition_fee),
        tuition_due_date: row.tuition_due_date || null,
        is_active: row.is_active === '활성'
      };
      
      console.log('수동 업데이트 데이터:', updateData);
      
      const response = await apiClient.updateStudent(row.id, updateData);
      console.log('수동 API 응답:', response);
      
      if (response.success) {
        toast({ title: '저장 완료', description: '학생 정보가 업데이트되었습니다.', variant: 'success' });
        fetchStudents();
      } else {
        throw new Error(response.message || '업데이트 실패');
      }
    } catch (e) {
      console.error('수동 편집 실패:', e);
      toast({ title: '저장 실패', description: String(e), variant: 'destructive' });
    }
  };

  // 셀 편집 완료 핸들러
  const handleCellEditComplete = async (params: any) => {
    try {
      console.log('셀 편집 완료:', params);
      
      // 편집 전 원본 데이터 찾기 (students 배열에서)
      const originalStudent = students.find(s => s.id === params.id);
      if (!originalStudent) return;
      
      // 원본 데이터를 DataGrid 형식으로 변환
      const originalRow = {
        id: originalStudent.id,
        name: originalStudent.name,
        email: originalStudent.email,
        phone: originalStudent.phone,
        grade: originalStudent.grade,
        tuition_fee: originalStudent.tuition_fee,
        tuition_due_date: originalStudent.tuition_due_date
          ? (typeof originalStudent.tuition_due_date === 'string'
              ? originalStudent.tuition_due_date.slice(0, 10)
              : originalStudent.tuition_due_date instanceof Date
                ? originalStudent.tuition_due_date.toISOString().slice(0, 10)
                : '')
          : '',
        is_active: originalStudent.is_active ? '활성' : '비활성',
        created_at: originalStudent.created_at?.slice(0, 10) || '',
      };
      
      // 현재 편집된 데이터 (params에서 가져오기)
      const currentRow = rows.find(row => row.id === params.id);
      if (!currentRow) return;
      
      // 편집된 필드만 업데이트된 새로운 행 데이터 생성
      const updatedRow = { ...originalRow };
      if (params.field && params.value !== undefined) {
        (updatedRow as any)[params.field] = params.value;
      }
      
      console.log('편집 전:', originalRow);
      console.log('편집 후:', updatedRow);
      
      // 편집 히스토리에 추가 (필드 정보 포함)
      addToHistory(originalRow, updatedRow, params.field);
      
      // 업데이트할 데이터 준비
      const updateData = {
        name: updatedRow.name,
        email: updatedRow.email,
        phone: updatedRow.phone,
        grade: updatedRow.grade,
        tuition_fee: Number(updatedRow.tuition_fee),
        tuition_due_date: updatedRow.tuition_due_date || null,
        is_active: updatedRow.is_active === '활성'
      };
      
      console.log('셀 편집 업데이트 데이터:', updateData);
      
      const response = await apiClient.updateStudent(params.id, updateData);
      console.log('셀 편집 API 응답:', response);
      
      if (response.success) {
        toast({ title: '저장 완료', description: `${params.field} 필드가 업데이트되었습니다.`, variant: 'success' });
        fetchStudents();
      } else {
        throw new Error(response.message || '업데이트 실패');
      }
    } catch (e) {
      console.error('셀 편집 실패:', e);
      toast({ title: '저장 실패', description: String(e), variant: 'destructive' });
    }
  };

  const apiRef = useGridApiRef();

  // 정렬/필터/컬럼 숨기기/컬럼 관리 상태
  const [sortModel, setSortModel] = useState<GridSortModel>([]);
  const [filterModel, setFilterModel] = useState<any>({ items: [] });
  const [columnVisibility, setColumnVisibility] = useState<Record<string, boolean>>({});
  const [isColumnPanelOpen, setIsColumnPanelOpen] = useState(false);
  const [hoveredColumn, setHoveredColumn] = useState<string | null>(null);

  // 샘플 학생 50명 자동 추가 (임시)
  const handleAddSampleStudents = async () => {
    const targetCount = 50;
    if (students.length >= targetCount) {
      toast({ title: '이미 50명 이상입니다.', variant: 'info' });
      return;
    }
    const toAdd = targetCount - students.length;
    const grades = ['1학년', '2학년', '3학년', '4학년'];
    for (let i = 0; i < toAdd; i++) {
      const idx = students.length + i + 1;
      const student = {
        name: `샘플학생${idx}`,
        email: `sample${idx}@test.com`,
        phone: `010-0000-${String(1000 + idx).slice(-4)}`,
        grade: grades[idx % grades.length],
        tuition_fee: 500000 + (idx % 5) * 10000,
        tuition_due_date: new Date(Date.now() + (idx % 30) * 86400000).toISOString().slice(0, 10),
        is_active: idx % 2 === 0
      };
      await apiClient.createStudent(student);
    }
    await fetchStudents();
    toast({ title: `${toAdd}명 샘플 학생 추가 완료!`, variant: 'success' });
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">학생 관리</h1>
          <Button disabled>새 학생 등록</Button>
        </div>
        <TableRowSkeleton rows={6} />
      </div>
    );
  }

  return (
    <ThemeProvider theme={createTheme()}>
      <CssBaseline />
      <GlobalStyles styles={{ '.MuiDataGrid-iconButtonContainer': { display: 'none !important' } }} />
      <Box sx={{ background: '#f8fafc', minHeight: '100vh', py: 6, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {/* 상단 바: 카드 스타일, 중앙 정렬 */}
        <Box sx={{ mb: 4, width: '100%', maxWidth: 1200 }}>
          <Paper elevation={3} sx={{ px: { xs: 2, md: 6 }, py: { xs: 2, md: 3 }, borderRadius: 3, width: '100%', background: (theme) => theme.palette.background.paper, boxShadow: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
              {/* 좌측: 아이콘 + 타이틀 + 서브타이틀 */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <SchoolRounded sx={{ fontSize: 44, color: 'primary.main' }} />
                <Box>
                  <Box sx={{ fontSize: 32, fontWeight: 700, color: 'text.primary', letterSpacing: -1 }}>학생 관리</Box>
                  <Box sx={{ fontSize: 16, color: 'text.secondary', mt: 0.5 }}>학생 정보를 효율적으로 관리하세요!</Box>
                </Box>
              </Box>
              {/* 우측: 요약 정보 + 샘플 추가 버튼 */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                <Chip icon={<PeopleAltRounded sx={{ color: 'primary.main' }} />} label={`전체 ${students.length}명`} sx={{ fontWeight: 500, bgcolor: 'primary.50', color: 'primary.main', px: 1.5 }} />
                <Chip icon={<PersonAddAlt1Rounded sx={{ color: 'success.main' }} />} label={`활성 ${students.filter(s => s.is_active).length}명`} sx={{ fontWeight: 500, bgcolor: 'success.50', color: 'success.main', px: 1.5 }} />
                <Chip icon={<PersonOffRounded sx={{ color: 'grey.700' }} />} label={`비활성 ${students.filter(s => !s.is_active).length}명`} sx={{ fontWeight: 500, bgcolor: 'grey.100', color: 'grey.700', px: 1.5 }} />
                {/* 최근 등록 학생 */}
                {students.length > 0 && (
                  <Chip label={`최근 등록: ${students[students.length-1].name}`} sx={{ fontWeight: 500, bgcolor: 'info.50', color: 'info.main', px: 1.5 }} />
                )}
                {/* 샘플 학생 추가 버튼 (임시) */}
              </Box>
            </Box>
          </Paper>
        </Box>
        {/* DataGrid 표: 넓게, 중앙 */}
        {/* 미리보기 표 위 버튼 그룹 + 검색창 + 새 학생 등록 버튼 */}
        <Box sx={{ width: '100%', maxWidth: 1200, mb: 1, display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 2, justifyContent: 'space-between' }}>
          {/* 왼쪽: 검색창 */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
            <TextField
              placeholder="이름, 이메일, 전화번호로 검색..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              sx={{ minWidth: 220, maxWidth: 400, background: '#fff', borderRadius: 1 }}
              size="small"
              variant="outlined"
            />
            <Box sx={{ fontSize: 14, color: 'text.secondary', ml: 1 }}>
              총 {students.length}명
            </Box>
          </Box>
          {/* 가운데: 버튼 그룹 */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Undo/Redo 버튼 */}
            <Tooltip title="실행 취소 (Ctrl+Z)"><span><IconButton onClick={handleUndo} disabled={historyIndex < 0} color="primary" sx={{ opacity: historyIndex < 0 ? 0.5 : 1 }}><Undo /></IconButton></span></Tooltip>
            <Tooltip title="다시 실행 (Ctrl+Shift+Z)"><span><IconButton onClick={handleRedo} disabled={historyIndex >= editHistory.length - 1} color="primary" sx={{ opacity: historyIndex >= editHistory.length - 1 ? 0.5 : 1 }}><Redo /></IconButton></span></Tooltip>
            <Tooltip title="저장"><IconButton color="secondary"><Save /></IconButton></Tooltip>
            <Tooltip title="행 추가"><IconButton onClick={handleAddRow} color="success"><Add /></IconButton></Tooltip>
            <Tooltip title="컬럼 추가"><IconButton onClick={handleAddColumn} color="info"><ViewColumn /></IconButton></Tooltip>
            <Tooltip title="선택된 행 삭제"><span><IconButton onClick={() => handleDeleteSelectedRows(selectedRows)} disabled={selectedRows.length === 0} color="error" sx={{ opacity: selectedRows.length === 0 ? 0.5 : 1 }}><Delete /></IconButton></span></Tooltip>
          </Box>
          {/* 오른쪽: 새 학생 등록 버튼 */}
          <MuiButton variant="contained" color="primary" onClick={() => setIsDialogOpen(true)} sx={{ fontWeight: 600, fontSize: 16, borderRadius: 2, boxShadow: 1, px: 3, py: 1 }}>
            새 학생 등록
          </MuiButton>
        </Box>
        <Box sx={{ width: '100%', maxWidth: 1200, mb: 8 }}>
          <Paper elevation={4} sx={{ width: '100%', p: 3, borderRadius: 4 }}>
            <Box sx={{ height: 540, width: '100%' }}>
              <DataGrid
                apiRef={apiRef}
                rows={rows}
                columns={orderedColumns.map(col => ({
                  ...col,
                  sortable: false,
                  renderHeader: (params) => {
                    const isEditing = editingHeader === col.field;
                    const currentHeader = col.headerName || '';
                    // 정렬 상태 확인
                    const sortItem = sortModel.find((s) => s.field === col.field);
                    const sortDirection = sortItem ? sortItem.sort : undefined;
                    const showSortIcon = !!sortDirection || hoveredColumn === col.field;
                    return (
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          width: '100%',
                          minWidth: '100%',
                          maxWidth: '100%',
                          cursor: 'default',
                          '&:hover': { background: 'rgba(0, 0, 0, 0.04)' }
                        }}
                        onDoubleClick={() => handleHeaderEditStart(col.field, currentHeader)}
                        onMouseEnter={() => setHoveredColumn(col.field)}
                        onMouseLeave={() => setHoveredColumn(null)}
                      >
                        {isEditing ? (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                            <TextField
                              value={headerEditValue}
                              onChange={(e) => setHeaderEditValue(e.target.value)}
                              size="small"
                              autoFocus
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  handleHeaderEditComplete(col.field);
                                } else if (e.key === 'Escape') {
                                  handleHeaderEditCancel();
                                }
                              }}
                              onBlur={() => handleHeaderEditComplete(col.field)}
                              sx={{ 
                                '& .MuiInputBase-input': { 
                                  fontSize: 'inherit', 
                                  fontWeight: 'inherit',
                                }
                              }}
                            />
                          </Box>
                        ) : (
                          <Box 
                            sx={{ 
                              display: 'flex', 
                              alignItems: 'center', 
                              width: '100%',
                              minWidth: 0,
                              maxWidth: '100%',
                              gap: 0.8,
                              cursor: 'grab',
                              '&:active': { cursor: 'grabbing' }
                            }}
                            draggable
                            onDragStart={(e) => handleDragStart(e, col.field)}
                            onDragOver={handleDragOver}
                            onDrop={(e) => handleDrop(e, col.field)}
                          >
                            <DragIndicator 
                              fontSize="small" 
                              sx={{ 
                                opacity: 0.3, 
                                flexShrink: 0,
                                flexGrow: 0,
                                minWidth: 28,
                                mr: 0.5
                              }} 
                            />
                            <span style={{ 
                              flex: '1 1 auto',
                              width: 'auto',
                              minWidth: 'fit-content',
                              maxWidth: '100%',
                              overflow: 'hidden', 
                              textOverflow: 'ellipsis', 
                              whiteSpace: 'nowrap',
                              fontSize: 'inherit',
                              fontWeight: 600
                            }}>
                              {currentHeader}
                            </span>
                            {/* 3점 아이콘: 항상 렌더링, id/actions 컬럼은 투명 처리 */}
                            <IconButton
                              size="small"
                              onClick={col.field !== 'id' && col.field !== 'actions' ? (e) => handleColumnMenuOpen(e, col.field) : undefined}
                              sx={{ 
                                opacity: col.field !== 'id' && col.field !== 'actions' ? 0.6 : 0,
                                visibility: col.field !== 'id' && col.field !== 'actions' ? 'visible' : 'hidden',
                                '&:hover': { opacity: 1 },
                                flexShrink: 0,
                                flexGrow: 0,
                                minWidth: 28,
                                ml: 0.5
                              }}
                            >
                              <MoreVert fontSize="small" />
                            </IconButton>
                            {/* 정렬 아이콘: 항상 렌더링, opacity/색상으로 상태 구분 */}
                            <IconButton
                              size="small"
                              sx={{
                                ml: 0.5,
                                background: sortDirection ? '#f3f4f6' : 'transparent',
                                transition: 'opacity 0.2s, color 0.2s',
                                p: 0.5,
                                flexShrink: 0,
                                flexGrow: 0,
                                minWidth: 28,
                                opacity: sortDirection || hoveredColumn === col.field ? 1 : 0.3
                              }}
                              onClick={() => {
                                if (!sortDirection) {
                                  setSortModel([{ field: col.field, sort: 'asc' }]);
                                } else if (sortDirection === 'asc') {
                                  setSortModel([{ field: col.field, sort: 'desc' }]);
                                } else {
                                  setSortModel([]);
                                }
                              }}
                            >
                              {sortDirection === 'asc' ? (
                                <ArrowUpward
                                  fontSize="small"
                                  sx={{
                                    color: 'primary.main',
                                    opacity: 1,
                                    transition: 'opacity 0.2s, color 0.2s',
                                  }}
                                />
                              ) : sortDirection === 'desc' ? (
                                <ArrowDownward
                                  fontSize="small"
                                  sx={{
                                    color: 'primary.main',
                                    opacity: 1,
                                    transition: 'opacity 0.2s, color 0.2s',
                                  }}
                                />
                              ) : (
                                <ArrowUpward
                                  fontSize="small"
                                  sx={{
                                    color: hoveredColumn === col.field ? '#bdbdbd' : 'inherit',
                                    opacity: hoveredColumn === col.field ? 1 : 0.3,
                                    transition: 'opacity 0.2s, color 0.2s',
                                  }}
                                />
                              )}
                            </IconButton>
                          </Box>
                        )}
                      </Box>
                    );
                  }
                }))}
                paginationModel={{ pageSize: 10, page: 0 }}
                pageSizeOptions={[10, 20, 50]}
                checkboxSelection
                disableRowSelectionOnClick={true}
                disableColumnMenu={true}

                editMode="cell"
                isCellEditable={(params) => params.field !== 'created_at' && params.field !== 'actions'}
                onCellClick={(params, event) => {
                  if (params.field !== 'created_at' && params.field !== 'actions') {
                    if (apiRef.current) {
                      apiRef.current.startCellEditMode({ id: params.id, field: params.field });
                    }
                  }
                }}
                onRowSelectionModelChange={handleRowSelectionChange}
                sx={{
                  fontSize: 17,
                  '& .MuiDataGrid-columnHeaders': { background: '#f3f4f6', fontWeight: 700, fontSize: 18 },
                  '& .MuiDataGrid-row:hover': { background: '#f1f5f9' },
                  '& .MuiDataGrid-cell': { py: 2 },
                  // 모든 컬럼 데이터 중앙 정렬
                  '& .text-center': { display: 'flex', alignItems: 'center', justifyContent: 'center' },
                  // 이메일 컬럼 특별 처리
                  '& .MuiDataGrid-cell[data-field="email"]': { 
                    wordBreak: 'break-all',
                    whiteSpace: 'normal',
                    lineHeight: 1.2,
                    minHeight: 'auto'
                  },
                  borderRadius: 3,
                }}
                processRowUpdate={handleRowUpdate}
                onCellEditStop={handleCellEditComplete}
                sortModel={sortModel}
                onSortModelChange={(model) => setSortModel(model)}
                filterModel={filterModel}
                columnVisibilityModel={columnVisibility}
                onColumnVisibilityModelChange={setColumnVisibility}
              />
            </Box>
          </Paper>
        </Box>
        {/* 학생 등록 다이얼로그, 기존 코드 유지 */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          {/* DialogTrigger 완전 제거: 상단 바 버튼에서만 다이얼로그 열림 */}
          <DialogContent>
            <DialogHeader>
              <DialogTitle>새 학생 등록</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="name">이름</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="email">이메일</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="phone">전화번호</Label>
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, phone: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="grade">학년</Label>
                <Input
                  id="grade"
                  value={formData.grade}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, grade: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="tuition_fee">수강료</Label>
                <Input
                  id="tuition_fee"
                  type="number"
                  value={formData.tuition_fee}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, tuition_fee: Number(e.target.value) })}
                  required
                  placeholder="예: 500000"
                />
              </div>
              <div>
                <Label htmlFor="tuition_due_date">납부일</Label>
                <Input
                  id="tuition_due_date"
                  type="date"
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, tuition_due_date: e.target.value })}
                  placeholder="선택사항"
                />
              </div>
              <Button type="submit" className="w-full">등록</Button>
            </form>
          </DialogContent>
        </Dialog>

        {/* AI 챗봇: 아래, 넓게, 중앙, 카드 스타일 */}
        <Box sx={{ width: '95vw', maxWidth: 1200, mx: 'auto', mb: 4 }}>
          <Paper elevation={3} sx={{ p: 4, borderRadius: 4 }}>
            {/* '새 학생 등록' 버튼/잔여 div 완전 제거 */}
            <AIChatBox />
          </Paper>
        </Box>

        {/* 컬럼 관리 메뉴 */}
        <Menu
          anchorEl={columnMenuAnchor}
          open={Boolean(columnMenuAnchor)}
          onClose={handleColumnMenuClose}
        >
          {/* 정렬/필터/숨기기/컬럼 관리 - 실제 동작 구현 */}
          <MenuItem>
            <ListItemIcon>
              <ArrowDownward fontSize="small" sx={{ cursor: 'pointer' }} onClick={() => {
                if (selectedColumn) {
                  setSortModel([{ field: selectedColumn, sort: 'desc' }]);
                }
                handleColumnMenuClose();
              }} />
            </ListItemIcon>
            <ListItemText>내림차순 정렬</ListItemText>
          </MenuItem>
          <MenuItem>
            <ListItemIcon>
              <Cancel fontSize="small" sx={{ cursor: 'pointer' }} onClick={() => {
                setSortModel([]);
                handleColumnMenuClose();
              }} />
            </ListItemIcon>
            <ListItemText>정렬 해제</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => {
            if (selectedColumn) {
              setColumnVisibility(prev => ({ ...prev, [selectedColumn]: false }));
            }
            handleColumnMenuClose();
          }}>
            <ListItemIcon><VisibilityOff fontSize="small" /></ListItemIcon>
            <ListItemText>컬럼 숨기기</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => {
            setIsColumnPanelOpen(true);
            handleColumnMenuClose();
          }}>
            <ListItemIcon><ViewColumn fontSize="small" /></ListItemIcon>
            <ListItemText>컬럼 관리</ListItemText>
          </MenuItem>
          {/* created_at 컬럼이 아닌 경우에만 편집 관련 메뉴 표시 */}
          {selectedColumn !== 'created_at' && (
            <Divider />
          )}
          {selectedColumn !== 'created_at' && (
            <MenuItem onClick={() => {
              if (selectedColumn) {
                handleDeleteColumn(selectedColumn);
              }
              handleColumnMenuClose();
            }}>
              <ListItemIcon>
                <Delete fontSize="small" />
              </ListItemIcon>
              <ListItemText>컬럼 삭제</ListItemText>
            </MenuItem>
          )}
          {selectedColumn !== 'created_at' && (
            <MenuItem onClick={() => {
              if (selectedColumn) {
                handleHeaderEditStart(selectedColumn, columns.find(col => col.field === selectedColumn)?.headerName || '');
              }
              handleColumnMenuClose();
            }}>
              <ListItemIcon>
                <Edit fontSize="small" />
              </ListItemIcon>
              <ListItemText>헤더 편집</ListItemText>
            </MenuItem>
          )}
        </Menu>

        {/* 컬럼 관리 패널(간단 다이얼로그) */}
        <Dialog open={isColumnPanelOpen} onOpenChange={setIsColumnPanelOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>컬럼 관리</DialogTitle>
            </DialogHeader>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
              {columns.map(col => (
                <Box key={col.field} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Checkbox
                    checked={columnVisibility[col.field] !== false}
                    onChange={(_, checked) => setColumnVisibility(prev => ({ ...prev, [col.field]: checked }))}
                  />
                  <span>{col.headerName}</span>
                </Box>
              ))}
            </Box>
          </DialogContent>
        </Dialog>
      </Box>
    </ThemeProvider>
  );
} 
"use client";

import React, { useState, useEffect, useMemo } from "react";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { Paper, Button as MuiButton, IconButton, Tooltip, Box } from "@mui/material";
import { Undo, Redo, Save, Add, Delete, MoreVert, ViewColumn, FileDownload } from "@mui/icons-material";
import ColumnSettingsDialog from "./ColumnSettingsDialog";
import { useHistoryManager } from "../../hooks/useHistoryManager";
import { EditEntityCommand, AddEntityCommand, DeleteEntityCommand } from "../../commands";
import { apiClient } from "../../lib/api-client";
import { ExcelDownloadButton } from "../ui/ExcelDownloadButton";

interface DataManagementTableProps {
  entityType: "students" | "teachers" | "materials" | "lectures";
  title: string;
  description?: string;
  icon?: React.ReactNode;
  columns: GridColDef[];
  data: any[];
  onRowUpdate: (newRow: any, oldRow: any) => Promise<any>;
  onAddRow: () => Promise<void>;
  onDeleteRow: (id: number) => Promise<void>;
  onAddSampleData?: () => Promise<void>;
  onSaveAll?: () => Promise<void>;
  pendingChanges?: any[];
  onColumnSettingsChange?: (visibleColumns: string[], columnOrder: string[], allColumns: GridColDef[]) => void;
  summaryStats: {
    total: number;
    active: number;
    inactive: number;
    recentRegistration?: string;
  };
}

export default function DataManagementTable({
  entityType,
  title,
  description,
  icon,
  columns,
  data,
  onRowUpdate,
  onAddRow,
  onDeleteRow,
  onAddSampleData,
  onSaveAll,
  pendingChanges = [],
  onColumnSettingsChange,
  summaryStats
}: DataManagementTableProps) {
  const [search, setSearch] = useState("");
  const [filteredData, setFilteredData] = useState<any[]>(data);
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [columnSettingsOpen, setColumnSettingsOpen] = useState(false);
  const [visibleColumns, setVisibleColumns] = useState<string[]>([]);
  const [columnOrder, setColumnOrder] = useState<string[]>([]);
  
  // 히스토리 관리자 사용
  const { executeCommand, undo, redo, canUndo, canRedo, historyInfo } = useHistoryManager();

  // pendingChanges에 따라 저장 상태 업데이트 (기존 호환성 유지)
  const hasUnsavedChanges = pendingChanges.length > 0 || historyInfo.total > 0;

  // 컬럼 설정 로드
  useEffect(() => {
    const savedSettings = localStorage.getItem(`column-settings-${entityType}`);
    if (savedSettings) {
      const settings = JSON.parse(savedSettings);
      setVisibleColumns(settings.visibleColumns || columns.map(col => col.field));
      setColumnOrder(settings.columnOrder || columns.map(col => col.field));
    } else {
      setVisibleColumns(columns.map(col => col.field));
      setColumnOrder(columns.map(col => col.field));
    }
  }, [columns, entityType]);

  // 필터링된 컬럼 생성
  const filteredColumns = useMemo(() => {
    return columns.filter(col => visibleColumns.includes(col.field));
  }, [columns, visibleColumns]);

  // 키보드 단축키 처리
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey) {
        if (event.key === 'z' && !event.shiftKey) {
          event.preventDefault();
          handleUndo();
        } else if (event.key === 'Z' && event.shiftKey) {
          event.preventDefault();
          handleRedo();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []); // 의존성 배열 제거하여 무한 루프 방지

  useEffect(() => {
    if (!search.trim()) {
      setFilteredData(data);
      return;
    }
    const searchLower = search.toLowerCase();
    setFilteredData(
      data.filter(item =>
        Object.values(item).some(
          v => typeof v === "string" && v.toLowerCase().includes(searchLower)
        )
      )
    );
  }, [data, search]);

  const getEntityLabel = () => {
    switch (entityType) {
      case "students": return "학생";
      case "teachers": return "강사";
      case "materials": return "교재";
      case "lectures": return "강의";
      default: return "항목";
    }
  };

  // Command Pattern 기반 편집 히스토리 관리
  const handleUndo = async () => {
    try {
      const success = await undo();
      if (success) {
        console.log('실행 취소 완료');
      } else {
        console.warn('실행 취소할 수 없습니다.');
      }
    } catch (error) {
      console.error('실행 취소 중 오류:', error);
      alert('실행 취소 중 오류가 발생했습니다.');
    }
  };

  const handleRedo = async () => {
    try {
      const success = await redo();
      if (success) {
        console.log('다시 실행 완료');
      } else {
        console.warn('다시 실행할 수 없습니다.');
      }
    } catch (error) {
      console.error('다시 실행 중 오류:', error);
      alert('다시 실행 중 오류가 발생했습니다.');
    }
  };

  const handleSave = async () => {
    if (!hasUnsavedChanges) return;
    
    setIsSaving(true);
    try {
      // 부모 컴포넌트의 저장 함수 호출
      if (onSaveAll) {
        await onSaveAll();
      }
      
      console.log('변경사항 저장 완료');
    } catch (error) {
      console.error('저장 중 오류:', error);
      alert('저장 중 오류가 발생했습니다.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteSelected = async () => {
    console.log('선택된 행들:', selectedRows);
    if (selectedRows.length === 0) {
      alert('삭제할 항목을 선택해주세요.');
      return;
    }
    
    if (confirm(`선택된 ${selectedRows.length}개 항목을 삭제하시겠습니까?`)) {
      try {
        console.log('삭제 시작:', selectedRows);
        for (const id of selectedRows) {
          console.log('삭제 중:', id);
          await onDeleteRow(id);
        }
        setSelectedRows([]);
        console.log('삭제 완료');
      } catch (error) {
        console.error('삭제 중 오류:', error);
        alert('삭제 중 오류가 발생했습니다.');
      }
    }
  };

  const handleRowSelectionChange = (newSelection: any) => {
    console.log('선택 변경:', newSelection);
    const selectionArray = Array.isArray(newSelection) ? newSelection : [];
    setSelectedRows(selectionArray);
    console.log('선택된 행 업데이트:', selectionArray);
  };

  const handleAddRow = async () => {
    try {
      await onAddRow();
    } catch (error) {
      console.error('추가 중 오류:', error);
    }
  };

  const handleColumnSettingsSave = (newVisibleColumns: string[], newColumnOrder: string[], allColumns: GridColDef[]) => {
    setVisibleColumns(newVisibleColumns);
    setColumnOrder(newColumnOrder);
    // 부모 컴포넌트에 컬럼 설정 변경 알림
    if (onColumnSettingsChange) {
      onColumnSettingsChange(newVisibleColumns, newColumnOrder, allColumns);
    }
  };

  return (
    <div className="container mx-auto p-6">
      {/* 헤더 영역 */}
      <div className="mb-8">
        <div className="bg-white/80 dark:bg-gray-800/50 backdrop-blur-md shadow-sm border border-white/20 rounded-2xl p-8 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              {icon && <div className="text-2xl">{icon}</div>}
              <div>
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white">{title}</h1>
                {description && <p className="text-lg text-gray-600 dark:text-gray-300 mt-2">{description}</p>}
              </div>
              <button 
                onClick={() => window.location.href = '/dashboard'}
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
              >
                대시보드
              </button>
            </div>
            
            {/* 통계 - 오른쪽에 배치 */}
            <div className="flex items-center gap-4">
              <div className="text-center bg-white/20 backdrop-blur-sm rounded-xl p-3 border border-white/30 hover:bg-white/30 transition-all duration-300">
                <div className="text-lg font-semibold text-gray-900 dark:text-white">{summaryStats.total}</div>
                <div className="text-xs text-gray-600 dark:text-gray-400 font-medium">전체</div>
              </div>
              <div className="text-center bg-green-50/50 backdrop-blur-sm rounded-xl p-3 border border-green-200/30 hover:bg-green-50/70 transition-all duration-300">
                <div className="text-lg font-semibold text-green-700 dark:text-green-400">{summaryStats.active}</div>
                <div className="text-xs text-green-600 dark:text-green-300 font-medium">활성</div>
              </div>
              <div className="text-center bg-red-50/50 backdrop-blur-sm rounded-xl p-3 border border-red-200/30 hover:bg-red-50/70 transition-all duration-300">
                <div className="text-lg font-semibold text-red-700 dark:text-red-400">{summaryStats.inactive}</div>
                <div className="text-xs text-red-600 dark:text-red-300 font-medium">비활성</div>
              </div>
              {summaryStats.recentRegistration && (
                <div className="text-center bg-purple-50/50 backdrop-blur-sm rounded-xl p-3 border border-purple-200/30 hover:bg-purple-50/70 transition-all duration-300">
                  <div className="text-sm font-semibold text-purple-700 dark:text-purple-400 truncate max-w-20">{summaryStats.recentRegistration}</div>
                  <div className="text-xs text-purple-600 dark:text-purple-300 font-medium">최근 등록</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 검색 및 액션 툴바 */}
      <div className="flex items-center justify-between mb-6 bg-white/60 dark:bg-gray-800/60 backdrop-blur-md rounded-xl p-4 border border-white/20">
        <div className="flex items-center gap-4">
          <div className="relative">
            <input
              type="text"
              placeholder="이름, 이메일, 전화번호로 검색"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="pl-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <span className="text-gray-600">{filteredData.length}명</span>
        </div>
        
        {/* 툴바 아이콘들 */}
        <div className="flex items-center gap-2">
          {/* 실행 취소 */}
          <Tooltip title="실행 취소 (Ctrl+Z)">
            <span>
              <IconButton 
                onClick={handleUndo} 
                disabled={!canUndo}
                color="primary"
              >
                <Undo />
              </IconButton>
            </span>
          </Tooltip>
          
          {/* 다시 실행 */}
          <Tooltip title="다시 실행 (Ctrl+Shift+Z)">
            <span>
              <IconButton 
                onClick={handleRedo} 
                disabled={!canRedo}
                color="primary"
              >
                <Redo />
              </IconButton>
            </span>
          </Tooltip>
          
          {/* 저장 */}
          <Tooltip title="저장">
            <span>
              <IconButton 
                onClick={handleSave} 
                disabled={!hasUnsavedChanges || isSaving}
                color="primary"
                sx={{ 
                  backgroundColor: hasUnsavedChanges ? '#8b5cf6' : 'transparent',
                  '&:hover': {
                    backgroundColor: hasUnsavedChanges ? '#7c3aed' : 'transparent'
                  }
                }}
              >
                <Save />
              </IconButton>
            </span>
          </Tooltip>
          
          {/* 추가 */}
          <Tooltip title="새 항목 추가">
            <IconButton onClick={handleAddRow} color="success">
              <Add />
            </IconButton>
          </Tooltip>
          
          {/* 레이아웃/보기 */}
          <Tooltip title="컬럼 설정">
            <IconButton 
              onClick={() => setColumnSettingsOpen(true)} 
              color="primary"
            >
              <ViewColumn />
            </IconButton>
          </Tooltip>
          
          {/* 삭제 */}
          <Tooltip title={`선택된 ${selectedRows.length}개 항목 삭제`}>
            <span>
              <IconButton 
                onClick={handleDeleteSelected} 
                disabled={selectedRows.length === 0}
                color="error"
                sx={{
                  position: 'relative',
                  '&:disabled': {
                    opacity: 0.5
                  }
                }}
              >
                <Delete />
                {selectedRows.length > 0 && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: -8,
                      right: -8,
                      backgroundColor: 'error.main',
                      color: 'white',
                      borderRadius: '50%',
                      width: 20,
                      height: 20,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.75rem',
                      fontWeight: 'bold'
                    }}
                  >
                    {selectedRows.length}
                  </Box>
                )}
              </IconButton>
            </span>
          </Tooltip>
          
          {/* 엑셀 다운로드 */}
          <ExcelDownloadButton 
            entityType={entityType} 
            data={filteredData}
            columns={filteredColumns}
          />
          
          {/* 추가 버튼들 */}
          <MuiButton variant="contained" color="primary" onClick={handleAddRow}>
            새 {getEntityLabel()} 등록
          </MuiButton>
          {onAddSampleData && (
            <MuiButton variant="outlined" onClick={onAddSampleData}>
              샘플 데이터 추가
            </MuiButton>
          )}
        </div>
      </div>

      {/* 데이터 테이블 */}
      <Paper elevation={2} className="w-full">
        <DataGrid
          rows={filteredData}
          columns={filteredColumns}
          initialState={{
            pagination: {
              paginationModel: { page: 0, pageSize: 10 },
            },
          }}
          pageSizeOptions={[10, 25, 50]}
          checkboxSelection
          disableRowSelectionOnClick
          rowSelectionModel={selectedRows}
          processRowUpdate={async (newRow, oldRow) => {
            // Command Pattern을 사용하여 편집 히스토리 관리
            const editCommand = new EditEntityCommand(
              entityType,
              newRow.id,
              oldRow,
              newRow,
              apiClient,
              (data) => {
                // 로컬 상태 업데이트 (부모 컴포넌트에서 처리)
                if (onRowUpdate) {
                  onRowUpdate(data, oldRow);
                }
              }
            );
            
            await executeCommand(editCommand);
            return newRow;
          }}
          onRowSelectionModelChange={handleRowSelectionChange}
          autoHeight
        />
      </Paper>

      {/* 컬럼 설정 다이얼로그 */}
      <ColumnSettingsDialog
        open={columnSettingsOpen}
        onClose={() => setColumnSettingsOpen(false)}
        columns={columns}
        onSave={handleColumnSettingsSave}
        entityType={entityType}
      />
    </div>
  );
} 
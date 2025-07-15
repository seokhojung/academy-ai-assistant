import React, { useState } from 'react';
import { DataGrid, GridColDef, GridPaginationModel } from '@mui/x-data-grid';
import { Box, Paper, IconButton, Tooltip } from '@mui/material';
import { Undo, Redo, Save, Add, Delete, ViewColumn } from '@mui/icons-material';

interface ExcelPreviewTableProps {
  title: string;
  rows: any[];
  columns: GridColDef[];
  onRowUpdate?: (newRow: any, oldRow: any) => Promise<any>;
  onAddRow?: () => void;
  onDeleteRow?: (id: number) => void;
  loading?: boolean;
  editHistory?: any[];
  historyIndex?: number;
  onUndo?: () => void;
  onRedo?: () => void;
  selectedRows?: number[];
  onRowSelectionChange?: (ids: number[]) => void;
}

const ExcelPreviewTable: React.FC<ExcelPreviewTableProps> = ({
  title,
  rows,
  columns,
  onRowUpdate,
  onAddRow,
  onDeleteRow,
  loading,
  editHistory,
  historyIndex,
  onUndo,
  onRedo,
  selectedRows,
  onRowSelectionChange,
}) => {
  const [paginationModel, setPaginationModel] = useState<GridPaginationModel>({
    page: 0,
    pageSize: 10,
  });

  return (
    <Paper elevation={4} sx={{ width: '100%', p: 3, borderRadius: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <span style={{ fontWeight: 700, fontSize: 22 }}>{title}</span>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {onUndo && (
            <Tooltip title="실행 취소"><span><IconButton onClick={onUndo} disabled={historyIndex === 0} color="primary"><Undo /></IconButton></span></Tooltip>
          )}
          {onRedo && (
            <Tooltip title="다시 실행"><span><IconButton onClick={onRedo} disabled={historyIndex === (editHistory?.length ?? 0) - 1} color="primary"><Redo /></IconButton></span></Tooltip>
          )}
          {onAddRow && (
            <Tooltip title="행 추가"><IconButton onClick={onAddRow} color="success"><Add /></IconButton></Tooltip>
          )}
          {onDeleteRow && selectedRows && (
            <Tooltip title="선택된 행 삭제"><span><IconButton onClick={() => selectedRows.forEach(id => onDeleteRow(id))} disabled={selectedRows.length === 0} color="error"><Delete /></IconButton></span></Tooltip>
          )}
        </Box>
      </Box>
      <Box sx={{ height: 540, width: '100%' }}>
        <DataGrid
          rows={rows}
          columns={columns}
          loading={loading}
          checkboxSelection={!!onDeleteRow}
          disableRowSelectionOnClick={true}
          disableColumnMenu={true}
          editMode={onRowUpdate ? 'cell' : undefined}
          processRowUpdate={onRowUpdate}
          onRowSelectionModelChange={onRowSelectionChange ? (model) => onRowSelectionChange(Array.isArray(model) ? model.map(Number) : []) : undefined}
          pagination
          paginationModel={paginationModel}
          onPaginationModelChange={setPaginationModel}
          pageSizeOptions={[10, 20, 50]}
          sx={{
            fontSize: 17,
            '& .MuiDataGrid-columnHeaders': { background: '#f3f4f6', fontWeight: 700, fontSize: 18 },
            '& .MuiDataGrid-row:hover': { background: '#f1f5f9' },
            '& .MuiDataGrid-cell': { py: 2 },
            borderRadius: 3,
          }}
        />
      </Box>
    </Paper>
  );
};

export default ExcelPreviewTable; 
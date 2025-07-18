"use client";

import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControlLabel,
  Checkbox,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  Box,
  Chip,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
} from "@mui/material";
import { 
  DragIndicator, 
  Visibility, 
  VisibilityOff, 
  Add as AddIcon,
  Delete as DeleteIcon 
} from "@mui/icons-material";
import { GridColDef } from "@mui/x-data-grid";

// 컬럼 추가 다이얼로그 컴포넌트
interface AddColumnDialogProps {
  open: boolean;
  onClose: () => void;
  onAdd: (column: GridColDef) => void;
  existingFields: string[];
}

function AddColumnDialog({ open, onClose, onAdd, existingFields }: AddColumnDialogProps) {
  const [fieldName, setFieldName] = useState("");
  const [headerName, setHeaderName] = useState("");
  const [fieldType, setFieldType] = useState("string");
  const [width, setWidth] = useState(150);
  const [editable, setEditable] = useState(true);

  const handleSubmit = () => {
    if (!fieldName.trim() || !headerName.trim()) {
      return;
    }

    const newColumn: GridColDef = {
      field: fieldName.trim(),
      headerName: headerName.trim(),
      width: width,
      editable: editable,
      type: fieldType as any,
    };

    onAdd(newColumn);
    
    // 폼 초기화
    setFieldName("");
    setHeaderName("");
    setFieldType("string");
    setWidth(150);
    setEditable(true);
    
    onClose();
  };

  const handleCancel = () => {
    setFieldName("");
    setHeaderName("");
    setFieldType("string");
    setWidth(150);
    setEditable(true);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleCancel} maxWidth="sm" fullWidth>
      <DialogTitle>
        새 컬럼 추가
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField
            label="필드명 (영문)"
            value={fieldName}
            onChange={(e) => setFieldName(e.target.value)}
            fullWidth
            required
            helperText="데이터베이스 필드명 (영문, 소문자, 언더스코어 사용)"
            error={existingFields.includes(fieldName)}
          />
          
          <TextField
            label="표시명 (한글)"
            value={headerName}
            onChange={(e) => setHeaderName(e.target.value)}
            fullWidth
            required
            helperText="테이블에 표시될 컬럼명"
          />
          
          <FormControl fullWidth>
            <InputLabel>필드 타입</InputLabel>
            <Select
              value={fieldType}
              onChange={(e) => setFieldType(e.target.value)}
              label="필드 타입"
            >
              <MenuItem value="string">텍스트</MenuItem>
              <MenuItem value="number">숫자</MenuItem>
              <MenuItem value="date">날짜</MenuItem>
              <MenuItem value="boolean">체크박스</MenuItem>
              <MenuItem value="singleSelect">선택박스</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            label="컬럼 너비"
            type="number"
            value={width}
            onChange={(e) => setWidth(Number(e.target.value))}
            fullWidth
            inputProps={{ min: 100, max: 500 }}
          />
          
          <FormControlLabel
            control={
              <Checkbox
                checked={editable}
                onChange={(e) => setEditable(e.target.checked)}
              />
            }
            label="편집 가능"
          />
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleCancel}>취소</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          disabled={!fieldName.trim() || !headerName.trim() || existingFields.includes(fieldName)}
        >
          추가
        </Button>
      </DialogActions>
    </Dialog>
  );
}

interface ColumnSettingsDialogProps {
  open: boolean;
  onClose: () => void;
  columns: GridColDef[];
  onSave: (visibleColumns: string[], columnOrder: string[], allColumns: GridColDef[]) => void;
  entityType: string;
}

export default function ColumnSettingsDialog({
  open,
  onClose,
  columns,
  onSave,
  entityType,
}: ColumnSettingsDialogProps) {
  const [visibleColumns, setVisibleColumns] = useState<string[]>([]);
  const [columnOrder, setColumnOrder] = useState<string[]>([]);
  const [allColumns, setAllColumns] = useState<GridColDef[]>([]);
  const [addColumnDialogOpen, setAddColumnDialogOpen] = useState(false);

  useEffect(() => {
    if (open) {
      // 로컬 스토리지에서 저장된 설정 불러오기
      const savedSettings = localStorage.getItem(`column-settings-${entityType}`);
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        const savedColumns = settings.allColumns || columns;
        setAllColumns(savedColumns);
        setVisibleColumns(settings.visibleColumns || savedColumns.map((col: GridColDef) => col.field));
        setColumnOrder(settings.columnOrder || savedColumns.map((col: GridColDef) => col.field));
      } else {
        // 기본값 설정
        setAllColumns(columns);
        setVisibleColumns(columns.map((col: GridColDef) => col.field));
        setColumnOrder(columns.map((col: GridColDef) => col.field));
      }
    }
  }, [open, columns, entityType]);

  const handleColumnToggle = (field: string) => {
    setVisibleColumns(prev => 
      prev.includes(field) 
        ? prev.filter(col => col !== field)
        : [...prev, field]
    );
  };

  const handleAddColumn = (newColumn: GridColDef) => {
    setAllColumns(prev => [...prev, newColumn]);
    setVisibleColumns(prev => [...prev, newColumn.field]);
    setColumnOrder(prev => [...prev, newColumn.field]);
  };

  const handleDeleteColumn = (field: string) => {
    // 기본 컬럼은 삭제 불가
    const isDefaultColumn = columns.some((col: GridColDef) => col.field === field);
    if (isDefaultColumn) {
      return;
    }

    setAllColumns(prev => prev.filter((col: GridColDef) => col.field !== field));
    setVisibleColumns(prev => prev.filter((col: string) => col !== field));
    setColumnOrder(prev => prev.filter((col: string) => col !== field));
  };

  const handleSave = () => {
    const settings = {
      visibleColumns,
      columnOrder,
      allColumns,
      timestamp: Date.now(),
    };
    
    // 로컬 스토리지에 저장
    localStorage.setItem(`column-settings-${entityType}`, JSON.stringify(settings));
    
    // 부모 컴포넌트에 전달
    onSave(visibleColumns, columnOrder, allColumns);
    onClose();
  };

  const handleReset = () => {
    setAllColumns(columns);
    setVisibleColumns(columns.map((col: GridColDef) => col.field));
    setColumnOrder(columns.map((col: GridColDef) => col.field));
  };

  const getColumnDisplayName = (field: string) => {
    const column = allColumns.find((col: GridColDef) => col.field === field);
    return column?.headerName || field;
  };

  const existingFields = allColumns.map((col: GridColDef) => col.field);

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                표시할 컬럼을 선택하고 순서를 조정하세요
              </Typography>
            </Box>
            <Tooltip title="새 컬럼 추가">
              <IconButton 
                onClick={() => setAddColumnDialogOpen(true)}
                color="primary"
                sx={{ 
                  bgcolor: 'primary.main', 
                  color: 'white',
                  '&:hover': { bgcolor: 'primary.dark' }
                }}
              >
                <AddIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              컬럼 설정
            </Typography>
            <Typography variant="subtitle2" gutterBottom>
              표시할 컬럼 ({visibleColumns.length}/{allColumns.length})
            </Typography>
          </Box>
          
          <List>
            {allColumns.map((column) => {
              const isVisible = visibleColumns.includes(column.field);
              const isEditable = column.editable !== false;
              const isDefaultColumn = columns.some((col: GridColDef) => col.field === column.field);
              
              return (
                <ListItem
                  key={column.field}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    backgroundColor: isVisible ? 'background.paper' : 'action.hover',
                  }}
                >
                  <ListItemIcon>
                    <DragIndicator color="action" />
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2">
                          {column.headerName || column.field}
                        </Typography>
                        {isEditable && (
                          <Chip 
                            label="편집 가능" 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                          />
                        )}
                        {!isDefaultColumn && (
                          <Chip 
                            label="사용자 정의" 
                            size="small" 
                            color="secondary" 
                            variant="outlined"
                          />
                        )}
                      </Box>
                    }
                    secondary={`필드명: ${column.field}`}
                  />
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={isVisible}
                          onChange={() => handleColumnToggle(column.field)}
                          icon={<VisibilityOff />}
                          checkedIcon={<Visibility />}
                        />
                      }
                      label=""
                    />
                    
                    {!isDefaultColumn && (
                      <Tooltip title="컬럼 삭제">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteColumn(column.field)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </ListItem>
              );
            })}
          </List>
          
          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary">
              • 체크된 컬럼만 테이블에 표시됩니다
              <br />
              • 편집 가능한 컬럼은 직접 수정할 수 있습니다
              <br />
              • 사용자 정의 컬럼은 삭제할 수 있습니다
              <br />
              • 설정은 자동으로 저장됩니다
            </Typography>
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleReset} color="secondary">
            기본값으로 초기화
          </Button>
          <Button onClick={onClose}>
            취소
          </Button>
          <Button onClick={handleSave} variant="contained" color="primary">
            저장
          </Button>
        </DialogActions>
      </Dialog>

      <AddColumnDialog
        open={addColumnDialogOpen}
        onClose={() => setAddColumnDialogOpen(false)}
        onAdd={handleAddColumn}
        existingFields={existingFields}
      />
    </>
  );
} 
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
} from "@mui/material";
import { DragIndicator, Visibility, VisibilityOff } from "@mui/icons-material";
import { GridColDef } from "@mui/x-data-grid";

interface ColumnSettingsDialogProps {
  open: boolean;
  onClose: () => void;
  columns: GridColDef[];
  onSave: (visibleColumns: string[], columnOrder: string[]) => void;
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

  useEffect(() => {
    if (open) {
      // 로컬 스토리지에서 저장된 설정 불러오기
      const savedSettings = localStorage.getItem(`column-settings-${entityType}`);
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        setVisibleColumns(settings.visibleColumns || columns.map(col => col.field));
        setColumnOrder(settings.columnOrder || columns.map(col => col.field));
      } else {
        // 기본값 설정
        setVisibleColumns(columns.map(col => col.field));
        setColumnOrder(columns.map(col => col.field));
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

  const handleSave = () => {
    const settings = {
      visibleColumns,
      columnOrder,
      timestamp: Date.now(),
    };
    
    // 로컬 스토리지에 저장
    localStorage.setItem(`column-settings-${entityType}`, JSON.stringify(settings));
    
    // 부모 컴포넌트에 전달
    onSave(visibleColumns, columnOrder);
    onClose();
  };

  const handleReset = () => {
    setVisibleColumns(columns.map(col => col.field));
    setColumnOrder(columns.map(col => col.field));
  };

  const getColumnDisplayName = (field: string) => {
    const column = columns.find(col => col.field === field);
    return column?.headerName || field;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6" component="div">
          컬럼 설정
        </Typography>
        <Typography variant="body2" color="text.secondary">
          표시할 컬럼을 선택하고 순서를 조정하세요
        </Typography>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            표시할 컬럼 ({visibleColumns.length}/{columns.length})
          </Typography>
        </Box>
        
        <List>
          {columns.map((column) => {
            const isVisible = visibleColumns.includes(column.field);
            const isEditable = column.editable !== false;
            
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
                    </Box>
                  }
                  secondary={`필드명: ${column.field}`}
                />
                
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
  );
} 
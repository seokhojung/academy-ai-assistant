import { useState } from 'react';
import * as XLSX from 'xlsx';

export type EntityType = 'students' | 'teachers' | 'materials' | 'lectures';

interface ExcelDownloadState {
  isDownloading: boolean;
  error: string | null;
  success: boolean;
}

export const useExcelDownload = () => {
  const [state, setState] = useState<ExcelDownloadState>({
    isDownloading: false,
    error: null,
    success: false,
  });

  const downloadExcel = async (entityType: EntityType, data: any[], columns: any[]) => {
    setState({
      isDownloading: true,
      error: null,
      success: false,
    });

    try {
      // 컬럼 매핑 (한글 컬럼명으로 변환)
      const columnMapping = getColumnMapping(entityType);
      
      // 데이터 변환 (한글 컬럼명으로)
      const transformedData = data.map(row => {
        const newRow: any = {};
        columns.forEach(col => {
          const field = col.field;
          const koreanField = (columnMapping as any)[field] || field;
          newRow[koreanField] = row[field];
        });
        return newRow;
      });

      // 엑셀 워크시트 생성
      const ws = XLSX.utils.json_to_sheet(transformedData);
      
              // 컬럼 너비 자동 조정
        const colWidths = columns.map(col => ({
          wch: Math.max(
            col.headerName?.length || col.field?.length || 10,
            ...transformedData.map(row => 
              String(row[(columnMapping as any)[col.field] || col.field] || '').length
            )
          )
        }));
      ws['!cols'] = colWidths;

      // 워크북 생성
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, getEntityTypeLabel(entityType));

      // 파일 다운로드
      const fileName = `${entityType}_${new Date().toISOString().split('T')[0]}.xlsx`;
      XLSX.writeFile(wb, fileName);

      // 백엔드 저장 기능은 현재 비활성화됨
      // 필요시 나중에 활성화 가능

      setState({
        isDownloading: false,
        error: null,
        success: true,
      });

      // 성공 상태를 3초 후 리셋
      setTimeout(() => {
        setState(prev => ({ ...prev, success: false }));
      }, 3000);

    } catch (error) {
      console.error('엑셀 다운로드 오류:', error);
      setState({
        isDownloading: false,
        error: error instanceof Error ? error.message : '다운로드 중 오류가 발생했습니다.',
        success: false,
      });
    }
  };

  const getColumnMapping = (entityType: EntityType) => {
    switch (entityType) {
      case 'students':
        return {
          'name': '이름',
          'email': '이메일',
          'phone': '전화번호',
          'grade': '학년',
          'tuition_fee': '수강료',
          'tuition_due_date': '납부일',
          'is_active': '상태',
          'created_at': '등록일'
        };
      case 'teachers':
        return {
          'name': '이름',
          'email': '이메일',
          'phone': '전화번호',
          'subject': '담당과목',
          'experience_years': '경력',
          'hourly_rate': '시급',
          'is_active': '상태',
          'created_at': '등록일'
        };
      case 'materials':
        return {
          'title': '제목',
          'subject': '과목',
          'grade_level': '학년',
          'publisher': '출판사',
          'price': '가격',
          'is_active': '상태',
          'created_at': '등록일'
        };
      case 'lectures':
        return {
          'title': '강의명',
          'teacher_name': '강사명',
          'subject': '과목',
          'grade_level': '학년',
          'schedule': '일정',
          'duration': '시간',
          'is_active': '상태',
          'created_at': '등록일'
        };
      default:
        return {};
    }
  };

  const getEntityTypeLabel = (entityType: EntityType) => {
    switch (entityType) {
      case 'students':
        return '학생';
      case 'teachers':
        return '강사';
      case 'materials':
        return '교재';
      case 'lectures':
        return '강의';
      default:
        return entityType;
    }
  };

  const resetState = () => {
    setState({
      isDownloading: false,
      error: null,
      success: false,
    });
  };

  return {
    ...state,
    downloadExcel,
    resetState,
  };
}; 
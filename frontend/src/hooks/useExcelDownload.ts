import { useState } from 'react';
import * as XLSX from 'xlsx';
import { apiClient } from '../lib/api-client';

export type EntityType = 'students' | 'teachers' | 'materials' | 'lectures';

interface ExcelDownloadState {
  isDownloading: boolean;
  error: string | null;
  success: boolean;
}

// 낙관적 업데이트 상태 확인 (전역 상태에서 가져오기)
const checkPendingChanges = (): boolean => {
  if (typeof window !== 'undefined') {
    const globalWindow = window as any;
    if (globalWindow.queryClient) {
      const mutationCache = globalWindow.queryClient.getMutationCache();
      const pendingMutations = mutationCache.getAll().filter(
        (mutation: any) => mutation.state.status === 'pending'
      );
      return pendingMutations.length > 0;
    }
  }
  return false;
};

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
      // 1. 낙관적 업데이트 대기 중인 변경사항 확인
      const hasPendingChanges = checkPendingChanges();
      let finalData = data;

      if (hasPendingChanges) {
        console.log('[Excel] 대기 중인 변경사항 감지, 서버에서 최신 데이터 조회');
        
        // 서버에서 최신 데이터 가져오기
        try {
          const serverData = await apiClient.getEntities(entityType);
          finalData = serverData;
          console.log('[Excel] 서버 최신 데이터 사용:', serverData.length, '개 항목');
        } catch (serverError) {
          console.warn('[Excel] 서버 데이터 조회 실패, 로컬 데이터 사용:', serverError);
          // 서버 오류 시 기존 로컬 데이터 사용 (fallback)
        }
      } else {
        console.log('[Excel] 대기 중인 변경사항 없음, 로컬 데이터 사용');
      }

      // 2. 컬럼 매핑 (한글 컬럼명으로 변환)
      const columnMapping = getColumnMapping(entityType);
      
      // 3. 데이터 변환 (한글 컬럼명으로)
      const transformedData = finalData.map(row => {
        const newRow: any = {};
        columns.forEach(col => {
          const field = col.field;
          const koreanField = (columnMapping as any)[field] || field;
          
          // 데이터 타입별 포맷팅
          let value = row[field];
          if (field === 'tuition_due_date' && value) {
            // 날짜 포맷팅
            value = new Date(value).toLocaleDateString('ko-KR');
          } else if (field === 'is_active') {
            // 활성 상태 한글 변환
            value = value ? '활성' : '비활성';
          } else if (field === 'created_at' && value) {
            // 생성일 포맷팅
            value = new Date(value).toLocaleDateString('ko-KR');
          }
          
          newRow[koreanField] = value;
        });
        return newRow;
      });

      // 4. 엑셀 워크시트 생성
      const ws = XLSX.utils.json_to_sheet(transformedData);
      
      // 5. 컬럼 너비 자동 조정
      const colWidths = columns.map(col => ({
        wch: Math.max(
          col.headerName?.length || col.field?.length || 10,
          ...transformedData.map(row => 
            String(row[(columnMapping as any)[col.field] || col.field] || '').length
          )
        )
      }));
      ws['!cols'] = colWidths;

      // 6. 워크북 생성
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, getEntityTypeLabel(entityType));

      // 7. 파일 다운로드
      const timestamp = new Date().toISOString().split('T')[0];
      const fileName = `${getEntityTypeLabel(entityType)}_${timestamp}.xlsx`;
      XLSX.writeFile(wb, fileName);

      setState({
        isDownloading: false,
        error: null,
        success: true,
      });

      console.log(`[Excel] 다운로드 완료: ${fileName} (${finalData.length}개 항목)`);

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
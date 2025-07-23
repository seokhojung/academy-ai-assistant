import React from 'react';
import { Download, CheckCircle, AlertCircle, Loader2, Clock } from 'lucide-react';
import { useExcelDownload, EntityType } from '../../hooks/useExcelDownload';
import { Button } from './Button';

interface ExcelDownloadButtonProps {
  entityType: EntityType;
  data: any[];
  columns: any[];
  className?: string;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  children?: React.ReactNode;
}

// 대기 중인 변경사항 확인
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

export const ExcelDownloadButton: React.FC<ExcelDownloadButtonProps> = ({
  entityType,
  data,
  columns,
  className = '',
  variant = 'outline',
  size = 'sm',
  children,
}) => {
  const { isDownloading, error, success, downloadExcel } = useExcelDownload();
  const hasPendingChanges = checkPendingChanges();

  const handleDownload = () => {
    downloadExcel(entityType, data, columns);
  };

  const getButtonContent = () => {
    if (isDownloading) {
      return (
        <>
          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          {hasPendingChanges ? '동기화 중...' : '다운로드 중...'}
        </>
      );
    }

    if (success) {
      return (
        <>
          <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
          다운로드 완료
        </>
      );
    }

    if (error) {
      return (
        <>
          <AlertCircle className="w-4 h-4 mr-2 text-red-500" />
          오류 발생
        </>
      );
    }

    if (hasPendingChanges) {
      return (
        <>
          <Clock className="w-4 h-4 mr-2 text-orange-500" />
          최신 데이터로 다운로드
        </>
      );
    }

    return (
      <>
        <Download className="w-4 h-4 mr-2" />
        {children || '엑셀 다운로드'}
      </>
    );
  };

  const getEntityTypeLabel = () => {
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

  const getTooltipText = () => {
    if (hasPendingChanges) {
      return `저장되지 않은 변경사항이 있습니다. 다운로드 시 서버에서 최신 데이터를 가져옵니다.`;
    }
    return `${getEntityTypeLabel()} 데이터를 엑셀 파일로 다운로드`;
  };

  return (
    <div className="flex flex-col gap-2">
      <Button
        onClick={handleDownload}
        disabled={isDownloading}
        variant={variant}
        size={size}
        className={`${className} ${error ? 'border-red-500 text-red-500' : ''} ${
          success ? 'border-green-500 text-green-500' : ''
        } ${hasPendingChanges ? 'border-orange-500 text-orange-600' : ''}`}
        title={getTooltipText()}
      >
        {getButtonContent()}
      </Button>
      
      {error && (
        <div className="text-xs text-red-500 flex items-center gap-1">
          <AlertCircle className="w-3 h-3" />
          {error}
        </div>
      )}
      
      {hasPendingChanges && !isDownloading && !error && (
        <div className="text-xs text-orange-600 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          저장되지 않은 변경사항 있음
        </div>
      )}
    </div>
  );
}; 
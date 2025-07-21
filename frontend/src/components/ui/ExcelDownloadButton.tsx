import React from 'react';
import { Download, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
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

  const handleDownload = () => {
    downloadExcel(entityType, data, columns);
  };

  const getButtonContent = () => {
    if (isDownloading) {
      return (
        <>
          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          다운로드 중...
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

  return (
    <div className="flex flex-col gap-2">
      <Button
        onClick={handleDownload}
        disabled={isDownloading}
        variant={variant}
        size={size}
        className={`${className} ${error ? 'border-red-500 text-red-500' : ''} ${
          success ? 'border-green-500 text-green-500' : ''
        }`}
        title={`${getEntityTypeLabel()} 데이터를 엑셀 파일로 다운로드`}
      >
        {getButtonContent()}
      </Button>
      
      {error && (
        <div className="text-xs text-red-500 flex items-center gap-1">
          <AlertCircle className="w-3 h-3" />
          {error}
        </div>
      )}
    </div>
  );
}; 
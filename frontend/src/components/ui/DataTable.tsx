import React from 'react';
import { TableData, TableStyleOptions } from '@/types/ai';

interface DataTableProps {
  data: TableData;
  styleOptions?: TableStyleOptions;
  className?: string;
}

const DataTable: React.FC<DataTableProps> = ({ 
  data, 
  styleOptions = {}, 
  className = "" 
}) => {
  console.log('[DataTable] 받은 데이터:', data);
  console.log('[DataTable] headers:', data.headers);
  console.log('[DataTable] rows:', data.rows);
  const {
    striped = true,
    hover = true,
    bordered = true,
    responsive = true,
    size = 'md'
  } = styleOptions;

  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  const tableClasses = [
    'w-full border-collapse',
    bordered ? 'border border-gray-300' : '',
    sizeClasses[size],
    className
  ].filter(Boolean).join(' ');

  const headerClasses = [
    'px-4 py-3 text-left font-semibold text-gray-800 dark:text-gray-200',
    bordered ? 'border-b border-gray-300 dark:border-gray-600' : '',
    'bg-blue-50 dark:bg-blue-900/20'
  ].filter(Boolean).join(' ');

  const cellClasses = [
    'px-4 py-3 text-gray-700 dark:text-gray-300',
    bordered ? 'border-b border-gray-200 dark:border-gray-700' : ''
  ].filter(Boolean).join(' ');

  const rowClasses = (index: number) => [
    hover ? 'hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-colors' : '',
    striped && index % 2 === 1 ? 'bg-gray-50 dark:bg-gray-800/50' : ''
  ].filter(Boolean).join(' ');

  const TableComponent = (
    <table className={tableClasses}>
      <thead>
        <tr>
          {data.headers.map((header, index) => (
            <th key={index} className={headerClasses}>
              {header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
        {data.rows.map((row, rowIndex) => (
          <tr key={rowIndex} className={rowClasses(rowIndex)}>
            {row.map((cell, cellIndex) => (
              <td key={cellIndex} className={cellClasses}>
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
      {data.footer && (
        <tfoot>
          <tr>
            <td 
              colSpan={data.headers.length} 
              className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700"
            >
              {data.footer}
            </td>
          </tr>
        </tfoot>
      )}
    </table>
  );

  if (responsive) {
    return (
      <div className="overflow-x-auto border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm">
        {TableComponent}
      </div>
    );
  }

  return TableComponent;
};

export default DataTable; 
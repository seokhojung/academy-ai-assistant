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
    bordered ? 'border border-gray-200' : '',
    sizeClasses[size],
    className
  ].filter(Boolean).join(' ');

  const headerClasses = [
    'px-4 py-3 text-left font-medium text-gray-700',
    bordered ? 'border-b border-gray-200' : '',
    'bg-gray-50'
  ].filter(Boolean).join(' ');

  const cellClasses = [
    'px-4 py-3 text-gray-900',
    bordered ? 'border-b border-gray-100' : ''
  ].filter(Boolean).join(' ');

  const rowClasses = (index: number) => [
    hover ? 'hover:bg-gray-50 transition-colors' : '',
    striped && index % 2 === 1 ? 'bg-gray-50' : ''
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
      <tbody className="bg-white divide-y divide-gray-200">
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
              className="px-4 py-2 text-sm text-gray-600 bg-gray-50 border-t border-gray-200"
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
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        {TableComponent}
      </div>
    );
  }

  return TableComponent;
};

export default DataTable; 
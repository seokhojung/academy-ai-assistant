'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

interface ChartData {
  name: string;
  value: number;
  [key: string]: any;
}

interface ChartProps {
  data: ChartData[];
  type: 'bar' | 'line' | 'pie';
  title: string;
  xAxisKey?: string;
  yAxisKey?: string;
  colors?: string[];
  className?: string;
}

const defaultColors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];

export const Chart: React.FC<ChartProps> = ({
  data,
  type,
  title,
  xAxisKey = 'name',
  yAxisKey = 'value',
  colors = defaultColors,
  className
}) => {
  const renderChart = () => {
    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xAxisKey} />
              <YAxis />
              <Tooltip />
              <Bar dataKey={yAxisKey} fill={colors[0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xAxisKey} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey={yAxisKey} stroke={colors[0]} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey={yAxisKey}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return (
    <motion.div
      className={`bg-white rounded-lg shadow-lg p-6 ${className || ''}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <motion.h3
        className="text-lg font-semibold mb-4 text-gray-800"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        {title}
      </motion.h3>
      
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        {renderChart()}
      </motion.div>

      {/* 데이터 요약 */}
      <motion.div
        className="mt-4 grid grid-cols-2 gap-4 text-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <div className="bg-gray-50 p-3 rounded">
          <div className="text-gray-600">총 데이터</div>
          <div className="text-xl font-bold text-gray-800">{data.length}</div>
        </div>
        <div className="bg-gray-50 p-3 rounded">
          <div className="text-gray-600">평균값</div>
          <div className="text-xl font-bold text-gray-800">
            {(data.reduce((sum, item) => sum + item[yAxisKey], 0) / data.length).toFixed(1)}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

// 특화된 차트 컴포넌트들
export const GradeChart: React.FC<{ data: ChartData[] }> = ({ data }) => (
  <Chart
    data={data}
    type="bar"
    title="학생별 성적 분포"
    xAxisKey="name"
    yAxisKey="grade"
    colors={['#3B82F6']}
  />
);

export const AttendanceChart: React.FC<{ data: ChartData[] }> = ({ data }) => (
  <Chart
    data={data}
    type="line"
    title="월별 출석률 추이"
    xAxisKey="month"
    yAxisKey="attendance"
    colors={['#10B981']}
  />
);

export const SubjectPieChart: React.FC<{ data: ChartData[] }> = ({ data }) => (
  <Chart
    data={data}
    type="pie"
    title="과목별 성적 분포"
    yAxisKey="value"
    colors={['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6']}
  />
); 
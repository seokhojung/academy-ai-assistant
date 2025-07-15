'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface GlassCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
  onClick?: () => void;
}

export function GlassCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  className,
  onClick,
}: GlassCardProps) {
  return (
    <motion.div
      className={cn(
        'relative overflow-hidden rounded-2xl p-6 cursor-pointer group',
        'bg-white/10 backdrop-blur-md border border-white/20',
        'hover:bg-white/15 hover:border-white/30 transition-all duration-300',
        'shadow-lg hover:shadow-xl',
        className
      )}
      whileHover={{ 
        scale: 1.02,
        y: -2,
      }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      {/* Glassmorphism 배경 효과 */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-white/10" />
      <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 opacity-50" />
      
      {/* 내용 */}
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </h3>
          {Icon && (
            <motion.div
              className="p-2 rounded-lg bg-white/10 border border-white/20"
              whileHover={{ rotate: 5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <Icon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </motion.div>
          )}
        </div>
        
        <div className="mb-2">
          <motion.div
            className="text-3xl font-bold text-gray-900 dark:text-white"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            {value}
          </motion.div>
        </div>
        
        {description && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            {description}
          </p>
        )}
        
        {trend && (
          <motion.div
            className="flex items-center space-x-1"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div
              className={cn(
                'flex items-center text-xs font-medium',
                trend.isPositive 
                  ? 'text-green-600 dark:text-green-400' 
                  : 'text-red-600 dark:text-red-400'
              )}
            >
              <span>{trend.isPositive ? '↗' : '↘'}</span>
              <span className="ml-1">{Math.abs(trend.value)}%</span>
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              지난 달 대비
            </span>
          </motion.div>
        )}
      </div>
      
      {/* 호버 효과 */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        initial={false}
      />
    </motion.div>
  );
}

// KPI 카드 그리드
export function KPIGrid({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {children}
    </div>
  );
}

// 통계 카드 (더 간단한 버전)
export function StatCard({
  title,
  value,
  icon: Icon,
  className,
}: {
  title: string;
  value: string | number;
  icon?: LucideIcon;
  className?: string;
}) {
  return (
    <motion.div
      className={cn(
        'bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border',
        'hover:shadow-md transition-shadow duration-200',
        className
      )}
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 300 }}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {value}
          </p>
        </div>
        {Icon && (
          <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
            <Icon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
          </div>
        )}
      </div>
    </motion.div>
  );
} 
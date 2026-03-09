/**
 * Bento Grid 布局组件
 * 浅色主题 + 4 列布局
 */

import React from 'react';
import { motion } from 'framer-motion';

interface BentoGridProps {
  children: React.ReactNode;
  className?: string;
}

export function BentoGrid({ children, className = '' }: BentoGridProps) {
  return (
    <div
      className={`
        grid grid-cols-1 lg:grid-cols-4 gap-4 px-4 py-6 min-h-screen
        bg-bento-bg
        ${className}
      `}
    >
      {children}
    </div>
  );
}

// Bento 卡片组件
interface BentoCardProps {
  children: React.ReactNode;
  className?: string;
  colSpan?: 1 | 2 | 3 | 4;
  rowSpan?: 1 | 2 | 3;
  title?: string;
  icon?: React.ReactNode;
}

export function BentoCard({
  children,
  className = '',
  colSpan = 1,
  rowSpan = 1,
  title,
  icon,
}: BentoCardProps) {
  const colClasses: Record<number, string> = {
    1: 'col-span-1',
    2: 'col-span-2',
    3: 'col-span-3',
    4: 'lg:col-span-4',  // 4列布局时占满整行
  };

  const rowClasses: Record<number, string> = {
    1: 'row-span-1',
    2: 'row-span-2',
    3: 'row-span-3',
  };

  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: '0 20px 30px rgba(0,0,0,0.04), 0 8px 12px rgba(0,0,0,0.05)' }}
      className={`
        rounded-3xl bg-white
        shadow-bento
        p-6 transition-all duration-300
        hover:shadow-bento-lg
        ${colClasses[colSpan]}
        ${rowClasses[rowSpan]}
        ${className}
      `}
    >
      {/* 标题区域 */}
      {title && (
        <div className="flex items-center gap-2 mb-4">
          {icon && (
            <span className="p-1.5 rounded-lg bg-gray-100 text-gray-600">
              {icon}
            </span>
          )}
          <h3 className="font-semibold text-gray-900">{title}</h3>
        </div>
      )}

      {/* 内容区域 */}
      {children}
    </motion.div>
  );
}

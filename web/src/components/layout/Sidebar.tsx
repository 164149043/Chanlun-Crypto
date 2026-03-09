/**
 * 左侧任务栏组件
 * 支持页面导航：AI分析、模型选择、K线图表、历史分析
 */

import { motion } from 'framer-motion';
import { Sparkles, Settings, BarChart3, Clock, CheckCircle } from 'lucide-react';
import { useAnalysisStore } from '../../stores/analysisStore';
import type { PageType } from '../../types/api';

interface SidebarItemProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  gradient: string;
  isActive: boolean;
  isDefault?: boolean;
  onClick: () => void;
  isDisabled?: boolean;
}

function SidebarItem({
  icon,
  title,
  description,
  gradient,
  isActive,
  isDefault,
  onClick,
  isDisabled,
}: SidebarItemProps) {
  return (
    <motion.button
      whileHover={!isDisabled ? { scale: 1.02 } : undefined}
      whileTap={!isDisabled ? { scale: 0.98 } : undefined}
      onClick={onClick}
      disabled={isDisabled}
      className={`
        w-full p-4 rounded-2xl text-left
        transition-all duration-200
        ${isActive
          ? 'bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-indigo-200'
          : 'bg-gray-50/50 border border-gray-100 hover:bg-gray-100/50'
        }
        ${isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
    >
      <div className="flex items-start gap-3">
        <div
          className={`
            p-2.5 rounded-xl text-white flex-shrink-0
            bg-gradient-to-br ${gradient}
          `}
        >
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-gray-900 text-sm">{title}</h4>
            {isDefault && (
              <span className="px-1.5 py-0.5 rounded text-xs bg-indigo-100 text-indigo-600">
                默认
              </span>
            )}
            {isActive && <CheckCircle className="w-4 h-4 text-indigo-500" />}
          </div>
          <p className="text-xs text-gray-500 mt-0.5">{description}</p>
        </div>
      </div>
    </motion.button>
  );
}

export function Sidebar() {
  const { currentPage, setCurrentPage, isAnalyzing } = useAnalysisStore();

  const items = [
    {
      id: 'analysis' as PageType,
      icon: <Sparkles className="w-4 h-4" />,
      title: 'AI分析',
      description: '三委员 + 裁决官分析',
      gradient: 'from-indigo-500 to-purple-500',
      isDefault: true,
    },
    {
      id: 'model' as PageType,
      icon: <Settings className="w-4 h-4" />,
      title: '模型选择',
      description: '配置 AI 模型参数',
      gradient: 'from-blue-500 to-blue-600',
    },
    {
      id: 'chart' as PageType,
      icon: <BarChart3 className="w-4 h-4" />,
      title: 'K线图表',
      description: '查看价格走势',
      gradient: 'from-purple-500 to-purple-600',
    },
    {
      id: 'history' as PageType,
      icon: <Clock className="w-4 h-4" />,
      title: '历史分析',
      description: '查看历史记录',
      gradient: 'from-orange-500 to-orange-600',
    },
  ];

  return (
    <div className="h-full flex flex-col">
      <div className="mb-4">
        <h3 className="font-semibold text-gray-900">任务面板</h3>
        <p className="text-xs text-gray-500 mt-1">选择功能模块</p>
      </div>
      <div className="flex flex-col gap-3 flex-1">
        {items.map((item) => (
          <SidebarItem
            key={item.id}
            {...item}
            isActive={currentPage === item.id}
            onClick={() => setCurrentPage(item.id)}
            isDisabled={isAnalyzing && item.id !== 'analysis'}
          />
        ))}
      </div>
    </div>
  );
}

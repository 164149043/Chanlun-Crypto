/**
 * 三委员卡片组件 - 展示各委员的分析结果
 * 浅色主题 + 温度滑块 + 自动高度
 */

import { motion } from 'framer-motion';
import { User, Brain, Shield, Zap } from 'lucide-react';
import { TemperatureSlider } from '../ui/TemperatureSlider';
import { useAnalysisStore } from '../../stores/analysisStore';
import type { CommitteeOutput } from '../../types/api';

interface CommitteeCardProps {
  committee: CommitteeOutput;
}

const COMMITTEE_CONFIG = {
  committee_a: {
    name: '委员A',
    subtitle: '保守派 · 风险厌恶',
    gradient: 'from-blue-500 to-cyan-500',
    color: '#3b82f6',
    icon: Shield,
  },
  committee_b: {
    name: '委员B',
    subtitle: '中立派 · 平衡分析',
    gradient: 'from-purple-500 to-pink-500',
    color: '#8b5cf6',
    icon: Brain,
  },
  committee_c: {
    name: '委员C',
    subtitle: '激进派 · 高风险偏好',
    gradient: 'from-orange-500 to-red-500',
    color: '#f97316',
    icon: Zap,
  },
} as const;

export function CommitteeCard({ committee }: CommitteeCardProps) {
  const { temperatures, setTemperature, isAnalyzing } = useAnalysisStore();
  const config = COMMITTEE_CONFIG[committee.id as keyof typeof COMMITTEE_CONFIG];
  const IconComponent = config?.icon || User;

  if (!config) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="rounded-3xl bg-white shadow-bento p-6 hover:shadow-bento-lg transition-all duration-300"
    >
      {/* 头部 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-xl bg-gradient-to-br ${config.gradient} text-white`}>
            <IconComponent className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{config.name}</h3>
            <p className="text-xs text-gray-500">{config.subtitle}</p>
          </div>
        </div>
        {committee.isStreaming && (
          <motion.span
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-600 text-xs font-medium"
          >
            分析中...
          </motion.span>
        )}
      </div>

      {/* 温度滑块 */}
      <div className="bg-gray-50 rounded-xl p-3 mb-4">
        <TemperatureSlider
          value={temperatures[committee.id as keyof typeof temperatures] || 0.5}
          onChange={(value) => setTemperature(committee.id as keyof typeof temperatures, value)}
          disabled={isAnalyzing}
          color={config.color}
        />
      </div>

      {/* 内容区 - 自动高度 */}
      <div className="text-sm text-gray-700 leading-relaxed">
        {committee.content ? (
          <div className="whitespace-pre-wrap">
            {committee.content}
            {committee.isStreaming && (
              <motion.span
                animate={{ opacity: [1, 0] }}
                transition={{ duration: 0.8, repeat: Infinity }}
                className="inline-block w-1 h-4 ml-0.5 rounded-sm bg-indigo-500"
              />
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-8 text-gray-400">
            <User className="w-8 h-8 mb-2 opacity-50" />
            <p className="text-sm">等待分析...</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}

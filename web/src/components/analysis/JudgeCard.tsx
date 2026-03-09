/**
 * 裁决官卡片组件 - 展示裁决官的综合结论
 * 浅色主题 + 温度滑块
 */

import { motion } from 'framer-motion';
import { Scale, Crown } from 'lucide-react';
import { TemperatureSlider } from '../ui/TemperatureSlider';
import { useAnalysisStore } from '../../stores/analysisStore';
import type { JudgeOutput } from '../../types/api';

interface JudgeCardProps {
  judge: JudgeOutput | null;
}

export function JudgeCard({ judge }: JudgeCardProps) {
  const { temperatures, setTemperature, isAnalyzing } = useAnalysisStore();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="rounded-3xl bg-white shadow-bento p-6 hover:shadow-bento-lg transition-all duration-300"
    >
      {/* 头部 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 text-white">
            <Crown className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              裁决官
              <Scale className="w-3.5 h-3.5 text-amber-500" />
            </h3>
            <p className="text-xs text-gray-500">综合决策 · 最终研判</p>
          </div>
        </div>
        {judge?.isStreaming && (
          <motion.span
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-600 text-xs font-medium"
          >
            裁决中...
          </motion.span>
        )}
      </div>

      {/* 温度滑块 */}
      <div className="bg-amber-50 rounded-xl p-3 mb-4">
        <TemperatureSlider
          value={temperatures.judge}
          onChange={(value) => setTemperature('judge', value)}
          disabled={isAnalyzing}
          color="#f59e0b"
        />
      </div>

      {/* 内容区 - 自动高度 */}
      <div className="text-sm text-gray-700 leading-relaxed">
        {judge?.content ? (
          <div className="whitespace-pre-wrap">
            {judge.content}
            {judge.isStreaming && (
              <motion.span
                animate={{ opacity: [1, 0] }}
                transition={{ duration: 0.8, repeat: Infinity }}
                className="inline-block w-1 h-4 ml-0.5 rounded-sm bg-amber-500"
              />
            )}
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center py-8 text-gray-400">
            <Scale className="w-8 h-8 mb-2 opacity-50" />
            <p className="text-sm">等待三委员分析完成...</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}

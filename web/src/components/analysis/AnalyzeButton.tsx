/**
 * 分析按钮组件
 * 浅色主题风格
 */

import { motion } from 'framer-motion';
import { Play, Square } from 'lucide-react';
import { useSSE } from '../../hooks/useSSE';
import { useAnalysisStore } from '../../stores/analysisStore';

interface AnalyzeButtonProps {
  disabled?: boolean
  symbol: string
}

export function AnalyzeButton({ disabled = false, symbol }: AnalyzeButtonProps) {
  const isAnalyzing = useAnalysisStore((state) => state.isAnalyzing)
  const { connect, disconnect } = useSSE()

  const handleStartAnalysis = () => {
    connect(symbol)
  }

  const handleStopAnalysis = () => {
    disconnect()
  }

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      disabled={disabled}
      onClick={isAnalyzing ? handleStopAnalysis : handleStartAnalysis}
      className={`
        flex items-center justify-center gap-2
        px-4 py-2.5 rounded-xl
        bg-white border border-gray-200
        text-gray-700 font-medium
        transition-all duration-200
        min-w-[160px]
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50 hover:border-gray-300 cursor-pointer'}
      `}
    >
      {isAnalyzing ? (
        <span className="flex items-center gap-2">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-4 h-4"
          >
            <Square className="w-4 h-4 text-gray-600" />
          </motion.div>
          <span className="text-sm text-gray-600">加载中...</span>
        </span>
      ) : (
        <span className="flex items-center gap-2">
          <Play className="w-4 h-4 text-gray-600" />
          开始分析
        </span>
      )}
    </motion.button>
  );
}

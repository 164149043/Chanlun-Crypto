/**
 * AI 分析总结卡片
 * 显示裁决官的综合分析总结（限制 800 字）
 */

import { motion } from 'framer-motion';
import { Sparkles, Crown } from 'lucide-react';

interface AISummaryCardProps {
  summary: string;
  isStreaming?: boolean;
}

const MAX_CHARS = 800;

export function AISummaryCard({ summary, isStreaming }: AISummaryCardProps) {
  // 限制显示约 800 字
  const displayText = summary.slice(0, MAX_CHARS);
  const isTruncated = summary.length > MAX_CHARS;

  return (
    <div className="h-full flex flex-col">
      {/* 头部 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 text-white">
            <Crown className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">AI 分析总结</h3>
            <p className="text-xs text-gray-500">裁决官综合研判</p>
          </div>
        </div>
        {isStreaming && (
          <motion.div
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="flex items-center gap-1.5 text-xs text-amber-600"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>生成中...</span>
          </motion.div>
        )}
      </div>

      {/* 内容区域 */}
      <div className="flex-1 min-h-0 bg-gradient-to-br from-amber-50/50 to-orange-50/50 rounded-2xl p-4 overflow-hidden">
        <div className="h-full overflow-y-auto custom-scrollbar">
          {summary ? (
            <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
              {displayText}
              {isTruncated && (
                <span className="text-gray-400 text-xs ml-1">
                  ... (内容已截断至 {MAX_CHARS} 字)
                </span>
              )}
              {isStreaming && (
                <motion.span
                  animate={{ opacity: [1, 0] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                  className="inline-block w-1 h-4 bg-amber-500 ml-0.5 rounded-sm"
                />
              )}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-400 text-sm">
              等待分析完成...
            </div>
          )}
        </div>
      </div>

      {/* 字数统计 */}
      {summary && (
        <div className="mt-3 flex justify-end">
          <span className="text-xs text-gray-400">
            {summary.length} / {MAX_CHARS} 字
          </span>
        </div>
      )}
    </div>
  );
}

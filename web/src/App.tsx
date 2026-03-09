/**
 * 主应用组件 - Bento Grid 布局
 * 浅色主题 + 4 列布局 + 页面导航
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';

// 组件
import { BentoGrid, BentoCard } from './components/layout/BentoGrid';
import { SymbolSelector } from './components/analysis/SymbolSelector';
import { AnalyzeButton } from './components/analysis/AnalyzeButton';
import { CommitteeCard } from './components/analysis/CommitteeCard';
import { JudgeCard } from './components/analysis/JudgeCard';
import { Sidebar } from './components/layout/Sidebar';
import { PositionInput } from './components/analysis/PositionInput';
import { ChartPage } from './components/chart/ChartPage';

// Store
import { useAnalysisStore } from './stores/analysisStore';

// Types
import type { Symbol } from './types/api';

function App() {
  const [symbol, setSymbol] = useState<Symbol>('BTCUSDT');

  const {
    currentPage,
    isAnalyzing,
    committees,
    judge,
    progress,
    stage,
    error,
  } = useAnalysisStore();

  // 渲染当前页面内容
  const renderPageContent = () => {
    switch (currentPage) {
      case 'analysis':
        return (
          <>
            {/* 控制面板 */}
            <BentoCard>
              <div className="flex items-end gap-4 flex-wrap">
                <div className="flex-1 min-w-[200px]">
                  <label className="block text-sm text-gray-500 mb-2">选择交易对</label>
                  <SymbolSelector
                    value={symbol}
                    onChange={setSymbol}
                    disabled={isAnalyzing}
                  />
                </div>
                <div className="flex-1 min-w-[200px]">
                  <label className="block text-sm text-gray-500 mb-2">持仓情况</label>
                  <PositionInput disabled={isAnalyzing} />
                </div>
                <div className="flex-shrink-0">
                  <label className="block text-sm text-gray-500 mb-2">&nbsp;</label>
                  <AnalyzeButton disabled={isAnalyzing} symbol={symbol} />
                </div>
              </div>

              {/* 状态显示 */}
              {stage !== 'idle' && stage !== 'complete' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4 p-3 rounded-xl bg-gray-50 border border-gray-100"
                >
                  <p className="text-sm text-gray-600">
                    {stage === 'fetching' && '📊 正在获取缠论数据...'}
                    {stage === 'committee_a' && '🔵 委员A 分析中...'}
                    {stage === 'committee_b' && '🟣 委员B 分析中...'}
                    {stage === 'committee_c' && '🟠 委员C 分析中...'}
                    {stage === 'judge' && '👑 裁决官综合分析中...'}
                    {stage === 'error' && `❌ 错误: ${error}`}
                  </p>
                </motion.div>
              )}

              {stage === 'complete' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4 p-3 rounded-xl bg-green-50 border border-green-200"
                >
                  <p className="text-sm text-green-600">✅ 分析完成</p>
                </motion.div>
              )}
            </BentoCard>

            {/* 三委员卡片 - 横向排列 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.values(committees).map((committee) => (
                <CommitteeCard key={committee.id} committee={committee} />
              ))}
            </div>

            {/* 裁决官卡片 */}
            <JudgeCard judge={judge} />
          </>
        );

      case 'model':
        return (
          <BentoCard>
            <div className="flex flex-col items-center justify-center py-20">
              <p className="text-sm text-gray-400">模型选择功能正在开发中...</p>
            </div>
          </BentoCard>
        );

      case 'chart':
        return <ChartPage symbol={symbol} />;

      case 'history':
        return (
          <BentoCard>
            <div className="flex flex-col items-center justify-center py-20">
              <p className="text-sm text-gray-400">历史分析功能正在开发中...</p>
            </div>
          </BentoCard>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-bento-bg">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-white/80 border-b border-gray-100">
        <div className="px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">多智能体缠论分析决策系统</h1>
                <p className="text-xs text-gray-500">多智能体 + 推理AI决策机制</p>
              </div>
            </div>

            {/* 进度条 */}
            {isAnalyzing && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                className="flex items-center gap-3"
              >
                <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                    style={{ width: `${progress * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">
                  {Math.round(progress * 100)}%
                </span>
              </motion.div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content - 4 列布局 */}
      <BentoGrid>
        {/* 左侧任务栏 - 占 1 列 */}
        <div className="lg:col-span-1">
          <BentoCard className="h-full">
            <Sidebar />
          </BentoCard>
        </div>

        {/* 右侧区域 - 占 3 列 */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          {renderPageContent()}
        </div>
      </BentoGrid>
    </div>
  );
}

export default App;

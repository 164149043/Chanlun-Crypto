/**
 * 分析状态管理 - Zustand Store
 */

import { create } from 'zustand';
import type { AnalysisStage, CommitteeOutput, JudgeOutput, PageType, PositionType } from '../types/api';

// 温度状态接口
interface Temperatures {
  committee_a: number;
  committee_b: number;
  committee_c: number;
  judge: number;
}

// 持仓状态接口
interface PositionState {
  type: PositionType;
  entryPrice: number | null;
}

interface AnalysisStore {
  // State
  currentPage: PageType;
  symbol: string | null;
  isAnalyzing: boolean;
  progress: number;
  stage: AnalysisStage;
  committees: Record<string, CommitteeOutput>;
  judge: JudgeOutput | null;
  error: string | null;
  temperatures: Temperatures;
  position: PositionState;

  // Actions
  setCurrentPage: (page: PageType) => void;
  setPositionType: (type: PositionType) => void;
  setEntryPrice: (price: number | null) => void;
  startAnalysis: (symbol: string) => void;
  updateProgress: (progress: number, stage: AnalysisStage, message: string) => void;
  updateCommittee: (id: string, content: string, isStreaming: boolean) => void;
  updateJudge: (content: string, isStreaming: boolean) => void;
  setError: (error: string) => void;
  completeAnalysis: () => void;
  reset: () => void;
  setTemperature: (id: keyof Temperatures, value: number) => void;
}

// 默认温度配置（来自 config.py）
const DEFAULT_TEMPERATURES: Temperatures = {
  committee_a: 0.4,  // 保守派
  committee_b: 0.6,  // 中立派
  committee_c: 0.7,  // 激进派
  judge: 0.3,        // 裁决官
};

const initialCommittees: Record<string, CommitteeOutput> = {
  committee_a: {
    id: 'committee_a',
    name: '委员A',
    role: '保守派',
    temperature: DEFAULT_TEMPERATURES.committee_a,
    content: '',
    isStreaming: false,
  },
  committee_b: {
    id: 'committee_b',
    name: '委员B',
    role: '中立派',
    temperature: DEFAULT_TEMPERATURES.committee_b,
    content: '',
    isStreaming: false,
  },
  committee_c: {
    id: 'committee_c',
    name: '委员C',
    role: '激进派',
    temperature: DEFAULT_TEMPERATURES.committee_c,
    content: '',
    isStreaming: false,
  },
};

export const useAnalysisStore = create<AnalysisStore>((set) => ({
  // Initial State
  currentPage: 'analysis',
  symbol: null,
  isAnalyzing: false,
  progress: 0,
  stage: 'idle',
  committees: initialCommittees,
  judge: null,
  error: null,
  temperatures: { ...DEFAULT_TEMPERATURES },
  position: { type: 'NONE', entryPrice: null },

  // Page Actions
  setCurrentPage: (page: PageType) => set({ currentPage: page }),

  // Position Actions
  setPositionType: (type: PositionType) =>
    set((state: AnalysisStore) => ({
      position: {
        ...state.position,
        type,
        entryPrice: type === 'NONE' ? null : state.position.entryPrice,
      },
    })),

  setEntryPrice: (price: number | null) =>
    set((state: AnalysisStore) => ({
      position: {
        ...state.position,
        entryPrice: price,
      },
    })),

  // Analysis Actions
  startAnalysis: (symbol: string) =>
    set({
      symbol,
      isAnalyzing: true,
      progress: 0,
      stage: 'fetching',
      committees: initialCommittees,
      judge: null,
      error: null,
    }),

  updateProgress: (progress: number, stage: AnalysisStage, _message: string) =>
    set({ progress, stage }),

  updateCommittee: (id: string, content: string, isStreaming: boolean) =>
    set((state: AnalysisStore) => ({
      committees: {
        ...state.committees,
        [id]: {
          ...state.committees[id],
          content,
          isStreaming,
        },
      },
    })),

  updateJudge: (content: string, isStreaming: boolean) =>
    set({
      judge: {
        content,
        isStreaming,
      },
    }),

  setError: (error: string) =>
    set({
      error,
      isAnalyzing: false,
      stage: 'error',
    }),

  completeAnalysis: () =>
    set((state: AnalysisStore) => ({
      isAnalyzing: false,
      stage: 'complete',
      progress: 1,
      committees: Object.fromEntries(
        Object.entries(state.committees).map(([key, value]) => [
          key,
          { ...value, isStreaming: false },
        ])
      ),
      judge: state.judge ? { ...state.judge, isStreaming: false } : null,
    })),

  reset: () =>
    set({
      symbol: null,
      isAnalyzing: false,
      progress: 0,
      stage: 'idle',
      committees: initialCommittees,
      judge: null,
      error: null,
      // 重置时保留温度设置，不重置为默认值
    }),

  setTemperature: (id: keyof Temperatures, value: number) =>
    set((state: AnalysisStore) => ({
      temperatures: {
        ...state.temperatures,
        [id]: value,
      },
    })),
}));

/**
 * API 类型定义
 */

export type Symbol = "BTCUSDT" | "ETHUSDT";

export interface KlineData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// 页面类型
export type PageType = 'analysis' | 'model' | 'chart' | 'history';

// 持仓类型
export type PositionType = 'NONE' | 'LONG' | 'SHORT';

// 持仓信息
export interface PositionInfo {
  position_type: PositionType;
  entry_price?: number;
}

export interface AnalysisRequest {
  symbol: Symbol;
  position?: PositionInfo;
}

export type AnalysisStage =
  | "idle"
  | "fetching"
  | "committee_a"
  | "committee_b"
  | "committee_c"
  | "judge"
  | "complete"
  | "error";

export interface SSEEvent {
  stage: AnalysisStage;
  message: string;
  content?: string;
  progress: number;
}

export interface CommitteeOutput {
  id: string;
  name: string;
  role: string;
  temperature: number;
  content: string;
  isStreaming: boolean;
}

export interface JudgeOutput {
  content: string;
  isStreaming: boolean;
}

export interface AnalysisState {
  symbol: Symbol | null;
  isAnalyzing: boolean;
  progress: number;
  stage: AnalysisStage;
  committees: Record<string, CommitteeOutput>;
  judge: JudgeOutput | null;
  error: string | null;
}

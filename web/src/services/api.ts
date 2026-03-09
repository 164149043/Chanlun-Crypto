/**
 * API 服务 - 与后端通信
 */

import type { KlineData, Symbol } from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function fetchSymbols(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/symbols`);
  if (!response.ok) {
    throw new Error(`获取交易对列表失败: ${response.status}`);
  }
  return response.json();
}

export async function fetchKlineData(
  symbol: Symbol,
  interval: string = '1d',
  limit: number = 200
): Promise<KlineData[]> {
  const response = await fetch(
    `${API_BASE}/api/kline/${symbol}?interval=${interval}&limit=${limit}`
  );
  if (!response.ok) {
    throw new Error(`获取 K 线数据失败: ${response.status}`);
  }
  return response.json();
}

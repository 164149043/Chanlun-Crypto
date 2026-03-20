/**
 * API 服务 - 与后端通信
 */

import type { KlineData, Symbol } from '../types/api';
import { useAuthStore } from '../stores/authStore';

// 生产环境(Vercel): VITE_API_BASE 为空字符串，使用相对路径
// 开发环境: VITE_API_BASE 为 http://localhost:8000
const API_BASE = import.meta.env.VITE_API_BASE ?? '';

// 获取认证请求头
function getAuthHeaders(): Record<string, string> {
  const token = useAuthStore.getState().token;
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

export async function fetchSymbols(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/symbols`, {
    headers: getAuthHeaders(),
  });
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
    `${API_BASE}/api/kline/${symbol}?interval=${interval}&limit=${limit}`,
    {
      headers: getAuthHeaders(),
    }
  );
  if (!response.ok) {
    throw new Error(`获取 K 线数据失败: ${response.status}`);
  }
  return response.json();
}

/**
 * SSE 连接 Hook - 处理 Server-Sent Events
 * 模块级变量确保切换页面时连接不中断
 */

import { useCallback } from 'react';
import { useAnalysisStore } from '../stores/analysisStore';
import { useAuthStore } from '../stores/authStore';
import type { SSEEvent, PositionInfo } from '../types/api';

// 生产环境(Vercel): VITE_API_BASE 为空字符串，使用相对路径
// 开发环境: VITE_API_BASE 为 http://localhost:8000
const API_BASE = import.meta.env.VITE_API_BASE ?? '';

// 模块级变量：不受组件卸载影响，切换页面时保持连接
let abortController: AbortController | null = null;

export function useSSE() {

  const {
    startAnalysis,
    updateProgress,
    updateCommittee,
    updateJudge,
    setError,
    completeAnalysis,
    position,
  } = useAnalysisStore();

  const connect = useCallback(async (symbol: string) => {
    // 断开现有连接
    disconnect();

    // 初始化状态
    startAnalysis(symbol);

    // 创建新的 AbortController
    abortController = new AbortController();

    // 构建请求体，包含持仓信息
    const requestBody: { symbol: string; position?: PositionInfo } = { symbol };

    // 如果有持仓，添加到请求体
    if (position.type !== 'NONE') {
      requestBody.position = {
        position_type: position.type,
        entry_price: position.entryPrice ?? undefined,
      };
    }

    // 获取认证 token
    const token = useAuthStore.getState().token;

    try {
      const response = await fetch(`${API_BASE}/api/analyze/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(requestBody),
        signal: abortController!.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      const readChunk = async () => {
        const { done, value } = await reader.read();

        if (done) {
          completeAnalysis();
          return;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // 保留最后一个不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event: SSEEvent = JSON.parse(line.slice(6));
              handleEvent(event);
            } catch (e) {
              console.error('解析 SSE 事件失败:', e, line);
            }
          }
        }

        // 继续读取
        await readChunk();
      };

      await readChunk();
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('SSE 连接已取消');
        return;
      }
      console.error('SSE 连接错误:', err);
      setError(err.message || '连接失败');
    }
  }, [startAnalysis, completeAnalysis, setError, position]);

  const handleEvent = useCallback((event: SSEEvent) => {
    updateProgress(event.progress, event.stage as any, event.message);

    switch (event.stage) {
      case 'committee_a':
        updateCommittee('committee_a', event.content || '', true);
        break;

      case 'committee_b':
        updateCommittee('committee_b', event.content || '', true);
        break;

      case 'committee_c':
        updateCommittee('committee_c', event.content || '', true);
        break;

      case 'judge':
        updateJudge(event.content || '', true);
        break;

      case 'complete':
        completeAnalysis();
        break;

      case 'error':
        setError(event.message);
        break;
    }
  }, [updateProgress, updateCommittee, updateJudge, completeAnalysis, setError]);

  const disconnect = useCallback(() => {
    if (abortController) {
      abortController.abort();
      abortController = null;
    }
  }, []);

  return { connect, disconnect };
}

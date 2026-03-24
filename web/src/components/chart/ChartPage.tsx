/**
 * K线图表页面
 * TradingView 实时行情图表 - 支持移动端自适应
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import type { Symbol } from '../../types/api';

import { BentoCard } from '../layout/BentoGrid';

interface ChartPageProps {
  symbol: Symbol;
}

// 检测是否为移动端
function isMobile(): boolean {
  if (typeof window === 'undefined') return false;
  return window.innerWidth < 768;
}

export function ChartPage({ symbol }: ChartPageProps) {
  const [localSymbol, setLocalSymbol] = useState<Symbol>(symbol);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const widgetRef = useRef<HTMLDivElement | null>(null);
  const [chartHeight, setChartHeight] = useState<number>(600);

  // 计算图表高度 - 自适应屏幕
  const calculateHeight = useCallback(() => {
    if (typeof window === 'undefined') return 600;

    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;

    // 移动端：使用视口高度减去 header(80px) 和 padding(48px)
    if (windowWidth < 768) {
      return Math.max(windowHeight - 128, 400);
    }

    // 桌面端：使用较大高度
    return Math.max(windowHeight - 200, 500);
  }, []);

  // 同步外部 symbol 变化
  useEffect(() => {
    setLocalSymbol(symbol);
  }, [symbol]);

  // 监听窗口大小变化
  useEffect(() => {
    const handleResize = () => {
      const newHeight = calculateHeight();
      setChartHeight(newHeight);
    };

    // 初始化高度
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [calculateHeight]);

  // 加载 TradingView 图表
  useEffect(() => {
    if (!containerRef.current) return;

    // 使用 requestAnimationFrame 确保 DOM 完全准备好
    const rafId = requestAnimationFrame(() => {
      if (!containerRef.current) return;

      // 清除之前的内容
      containerRef.current.innerHTML = '';

      // 创建widget容器
      const widgetContainer = document.createElement('div');
      widgetContainer.className = 'tradingview-widget-container__widget';
      widgetContainer.style.height = 'calc(100% - 24px)';
      widgetContainer.style.width = '100%';

      // 创建版权链接 - 移动端缩小高度
      const copyrightDiv = document.createElement('div');
      copyrightDiv.className = 'tradingview-widget-container__copyright';
      copyrightDiv.style.height = isMobile() ? '24px' : '32px';
      copyrightDiv.style.width = '100%';
      copyrightDiv.style.fontSize = isMobile() ? '10px' : '12px';
      copyrightDiv.style.display = 'flex';
      copyrightDiv.style.alignItems = 'center';
      copyrightDiv.style.justifyContent = 'center';

      // 创建链接
      const link = document.createElement('a');
      link.href = `https://cn.tradingview.com/symbols/${localSymbol}/?exchange=BINANCE`;
      link.rel = 'noopener nofollow';
      link.target = '_blank';

      const span = document.createElement('span');
      span.className = 'blue-text';
      span.textContent = 'Track all markets on TradingView';
      link.appendChild(span);
      copyrightDiv.appendChild(link);

      // 创建脚本
      const script = document.createElement('script');
      script.type = 'text/javascript';
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
      script.async = true;

      // 配置参数 - 移动端优化
      const tradingViewSymbol = `BINANCE:${localSymbol}.P`;
      const mobile = isMobile();

      const config = {
        autosize: true,
        allow_symbol_change: true,
        calendar: false,
        details: false,
        // 移动端隐藏侧边工具栏，节省空间
        hide_side_toolbar: mobile,
        // 移动端可以隐藏顶部工具栏以节省空间
        hide_top_toolbar: false,
        hide_legend: false,
        hide_volume: false,
        hotlist: false,
        interval: '60',
        locale: 'zh_CN',
        symbol: tradingViewSymbol,
        theme: 'light',
        timezone: 'Asia/Shanghai',
        watchlist: [
          'BINANCE:BTCUSDT.P',
          'BINANCE:ETHUSDT.P',
          'BINANCE:BNBUSDT.P',
          'BINANCE:SOLUSDT.P',
          'BINANCE:XRPUSDT.P',
        ],
      };

      script.textContent = JSON.stringify(config);
      widgetContainer.appendChild(script);
      containerRef.current.appendChild(widgetContainer);
      containerRef.current.appendChild(copyrightDiv);

      // 保存引用
      widgetRef.current = widgetContainer;
    });

    return () => {
      cancelAnimationFrame(rafId);
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [localSymbol, chartHeight]);

  return (
    <BentoCard className="h-full flex-1 flex flex-col p-2 md:p-6">
      <div
        ref={containerRef}
        className="w-full flex-1"
        style={{ height: `${chartHeight}px`, minHeight: '400px' }}
      />
    </BentoCard>
  );
}

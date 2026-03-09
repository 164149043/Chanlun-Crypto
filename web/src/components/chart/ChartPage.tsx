/**
 * K线图表页面
 * TradingView 实时行情图表
 */

import { useEffect, useRef, useState } from 'react';
import type { Symbol } from '../../types/api';

import { BentoCard } from '../layout/BentoGrid';

interface ChartPageProps {
  symbol: Symbol;
}

export function ChartPage({ symbol }: ChartPageProps) {
  const [localSymbol, setLocalSymbol] = useState<Symbol>(symbol);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // 同步外部 symbol 变化
  useEffect(() => {
    setLocalSymbol(symbol);
  }, [symbol]);

  // 加载 TradingView 图表
  useEffect(() => {
    if (!containerRef.current) return;

    // 清除之前的内容
    containerRef.current.innerHTML = '';

    // 创建widget容器
    const widgetContainer = document.createElement('div');
    widgetContainer.className = 'tradingview-widget-container__widget';
    widgetContainer.style.height = 'calc(100% - 32px)';
    widgetContainer.style.width = '100%';

    // 创建版权链接
    const copyrightDiv = document.createElement('div');
    copyrightDiv.className = 'tradingview-widget-container__copyright';
    copyrightDiv.style.height = '32px';
    copyrightDiv.style.width = '100%';

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

    // 配置参数
    // 将 BTCUSDT 格式转换为 TradingView 格式: BINANCE:BTCUSDT.P (永续合约)
    const tradingViewSymbol = `BINANCE:${localSymbol}.P`;
    const config = {
      autosize: true,
      allow_symbol_change: true,
      calendar: false,
      details: false,
      hide_side_toolbar: false,
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

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [localSymbol]);

  return (
    <BentoCard className="h-full">
      <div ref={containerRef} className="h-full w-full min-h-[500px]" />
    </BentoCard>
  );
}

#!/usr/bin/env python3
"""
Binance 加密货币缠论分析 + AI 预测系统
"""

import sys
from datetime import datetime, timedelta
from typing import List

from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import KL_TYPE

from DataAPI.binanceAPI import BinanceAPI
from result_formatter import format_chan_result, format_full_report
from ai_analyzer import analyze_with_deepseek
from config import (
    DEEPSEEK_API_KEY,
    PROXY_URL,
    SYMBOLS,
    PERIOD_NAMES,
    PRINT_RAW_DATA,
    SAVE_TO_FILE,
    OUTPUT_FILE,
)

# 要分析的周期
PERIODS: List[KL_TYPE] = [
    KL_TYPE.K_DAY,
    KL_TYPE.K_4H,
    KL_TYPE.K_60M,
    KL_TYPE.K_15M,
]


def print_banner():
    print()
    print("=" * 60)
    print("  Binance 缠论分析 + AI 预测")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def select_symbol() -> List[str]:
    """选择交易对"""
    print("\n选择交易对:")
    print("  1. BTCUSDT")
    print("  2. ETHUSDT")
    print("  3. 全部")
    print()

    while True:
        try:
            choice = input("请选择 (1/2/3，回车默认全部): ").strip()

            if not choice or choice == "3":
                print("已选择: BTCUSDT, ETHUSDT")
                return ["BTCUSDT", "ETHUSDT"]
            elif choice == "1":
                print("已选择: BTCUSDT")
                return ["BTCUSDT"]
            elif choice == "2":
                print("已选择: ETHUSDT")
                return ["ETHUSDT"]
            else:
                print("请输入 1、2 或 3")

        except KeyboardInterrupt:
            print("\n用户取消")
            sys.exit(0)


def analyze_symbol(symbol: str) -> str:
    """分析单个交易对"""
    results = []

    for kl_type in PERIODS:
        period_name = PERIOD_NAMES.get(kl_type.name, kl_type.name)
        print(f"  [{symbol}] 分析 {period_name}...")

        try:
            # 日线获取120天，其他周期获取60天
            days = 120 if kl_type == KL_TYPE.K_DAY else 60
            begin_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            chan = CChan(
                code=symbol,
                data_src="custom:binanceAPI.BinanceAPI",
                begin_time=begin_date,
                lv_list=[kl_type],
                config=CChanConfig(),
            )

            result = format_chan_result(chan, symbol, period_name)
            results.append(result)
            print(f"  [{symbol}] {period_name} 完成")

        except Exception as e:
            results.append(f"## {symbol} - {period_name}\n\n失败: {e}\n")
            print(f"  [{symbol}] {period_name} 失败: {e}")

    return "\n---\n".join(results)


def main():
    # 设置代理（如果配置了）
    if PROXY_URL:
        BinanceAPI.set_proxy(PROXY_URL)

    print_banner()

    # 选择交易对
    symbols = select_symbol()
    print(f"\n分析: {', '.join(symbols)}")

    # 提示 API 配置
    if not DEEPSEEK_API_KEY:
        print("\n[提示] 未配置 DEEPSEEK_API_KEY，只输出缠论数据")

    # 分析
    all_results = []
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"分析 {symbol}...")
        print("=" * 60)
        all_results.append(analyze_symbol(symbol))

    # 输出
    full_report = format_full_report(all_results)

    if PRINT_RAW_DATA:
        print("\n" + "=" * 60)
        print("缠论数据")
        print("=" * 60)
        print(full_report)

    # AI 分析
    if DEEPSEEK_API_KEY:
        print("\n" + "=" * 60)
        print("AI 分析...")
        print("=" * 60)
        ai_result = analyze_with_deepseek(full_report, DEEPSEEK_API_KEY)
        print(ai_result)

        if SAVE_TO_FILE:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(f"# 分析报告\n\n{full_report}\n\n## AI\n\n{ai_result}")
            print(f"\n已保存: {OUTPUT_FILE}")

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)

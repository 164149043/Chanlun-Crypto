#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 策略引擎 - 三委员 + 裁决官机制

架构：
    缠论数据 → 三委员独立分析 → 裁决官综合推理 → 最终策略

设计原则：
    - 第一层（委员）：自由表达，独立推理
    - 第二层（裁决官）：只能基于三份报告推理，不能看原始数据
"""

import concurrent.futures
import io
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from config import DEEPSEEK_API_KEY, PROXY_URL, COMMITTEE_CONFIG
from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import KL_TYPE
from DataAPI.binanceAPI import BinanceAPI
from result_formatter import format_chan_result

# Windows 控制台编码处理
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ============================================
# 常量配置
# ============================================
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_MODEL = "deepseek-reasoner"
MAX_RETRIES = 3

PERIODS = [
    (KL_TYPE.K_DAY, "D1"),
    (KL_TYPE.K_4H, "H4"),
    (KL_TYPE.K_60M, "H1"),
    (KL_TYPE.K_15M, "M15"),
]

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ============================================
# 数据获取
# ============================================

def select_symbol() -> List[str]:
    """选择交易对"""
    print("\n选择交易对:")
    print("  1. BTCUSDT")
    print("  2. ETHUSDT")
    print("  3. 全部")
    while True:
        try:
            choice = input("请选择 (1/2/3，回车默认 BTCUSDT): ").strip()
            if not choice or choice == "1":
                return ["BTCUSDT"]
            if choice == "2":
                return ["ETHUSDT"]
            if choice == "3":
                return ["BTCUSDT", "ETHUSDT"]
            print("请输入 1/2/3")
        except KeyboardInterrupt:
            print("\n用户取消")
            sys.exit(0)


def select_position() -> Optional[Dict[str, Any]]:
    """
    选择持仓信息

    Returns:
        持仓信息字典，格式: {"type": "LONG/SHORT", "entry_price": xxx}
        如果没有仓位则返回 None
    """
    print("\n持仓状态:")
    print("  1. 没有仓位")
    print("  2. 做多 (LONG)")
    print("  3. 做空 (SHORT)")

    while True:
        try:
            choice = input("请选择 (1/2/3，回车默认没有仓位): ").strip()
            if not choice or choice == "1":
                return None
            if choice == "2":
                pos_type = "LONG"
                break
            if choice == "3":
                pos_type = "SHORT"
                break
            print("请输入 1/2/3")
        except KeyboardInterrupt:
            print("\n用户取消")
            sys.exit(0)

    # 输入开仓均价
    while True:
        try:
            price_input = input(f"请输入开仓均价: ").strip()
            if not price_input:
                print("开仓均价不能为空")
                continue
            entry_price = float(price_input)
            if entry_price <= 0:
                print("开仓均价必须大于 0")
                continue
            return {"type": pos_type, "entry_price": entry_price}
        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            print("\n用户取消")
            sys.exit(0)


def get_chanlun_data_single(symbol: str, kl_type: KL_TYPE, period_name: str) -> Dict[str, Any]:
    """获取单个周期的缠论数据"""
    result: Dict[str, Any] = {"period": period_name}
    try:
        days = 120 if kl_type == KL_TYPE.K_DAY else 60
        begin_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        chan = CChan(
            code=symbol,
            data_src="custom:binanceAPI.BinanceAPI",
            begin_time=begin_date,
            lv_list=[kl_type],
            config=CChanConfig(),
        )
        result["formatted_text"] = format_chan_result(chan, symbol, period_name)

        kl_datas = chan.kl_datas
        kl = kl_datas.get(kl_type) if isinstance(kl_datas, dict) else None
        if not kl or not getattr(kl, "lst", None):
            return result

        # 提取K线数据
        last_merged = kl.lst[-1]
        if getattr(last_merged, "lst", None):
            last_unit = last_merged.lst[-1]
            result["current_price"] = float(last_unit.close)
            result["open"] = float(last_unit.open)
            result["high"] = float(last_unit.high)
            result["low"] = float(last_unit.low)
            if hasattr(last_unit, "macd") and last_unit.macd:
                try:
                    result["macd"] = float(last_unit.macd.macd)
                except Exception:
                    pass

        # 最近高低点
        klines = kl.lst[-20:] if len(kl.lst) >= 20 else kl.lst
        highs = [float(k.high) for k in klines if hasattr(k, "high")]
        lows = [float(k.low) for k in klines if hasattr(k, "low")]
        if highs:
            result["recent_high"] = max(highs)
        if lows:
            result["recent_low"] = min(lows)

        # 笔方向
        if getattr(kl, "bi_list", None):
            last_bi = kl.bi_list[-1]
            bi_dir = str(getattr(last_bi, "dir", "")).lower()
            result["bi_direction"] = "up" if "up" in bi_dir else "down"
            if getattr(last_bi, "begin_klc", None) and hasattr(last_bi.begin_klc, "low"):
                result["bi_start"] = float(last_bi.begin_klc.low)
            if getattr(last_bi, "end_klc", None) and hasattr(last_bi.end_klc, "low"):
                result["bi_end"] = float(last_bi.end_klc.low)

        # 线段方向
        if getattr(kl, "seg_list", None):
            last_seg = kl.seg_list[-1]
            seg_dir = str(getattr(last_seg, "dir", "")).lower()
            result["seg_direction"] = "up" if "up" in seg_dir else "down"

        # 中枢位置
        if getattr(kl, "zs_list", None):
            last_zs = kl.zs_list[-1]
            result["zs_high"] = float(getattr(last_zs, "zg", 0) or 0)
            result["zs_low"] = float(getattr(last_zs, "zd", 0) or 0)
            current = result.get("current_price", 0)
            if current and result["zs_high"] and result["zs_low"]:
                if current > result["zs_high"]:
                    result["zs_position"] = "above"
                elif current < result["zs_low"]:
                    result["zs_position"] = "below"
                else:
                    result["zs_position"] = "inside"
    except Exception as e:
        logger.warning(f"获取 {period_name} 数据失败: {e}")
    return result


def get_multi_cycle_data(symbol: str) -> Dict[str, Any]:
    """获取多周期缠论数据"""
    logger.info(f"获取 {symbol} 多周期缠论数据")
    result: Dict[str, Any] = {
        "symbol": symbol,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market_type": "crypto_perpetual",
        "cycles": {},
    }
    current_price = 0.0
    for kl_type, period_name in PERIODS:
        print(f"  分析 {period_name} ...")
        cycle_data = get_chanlun_data_single(symbol, kl_type, period_name)
        result["cycles"][period_name] = cycle_data
        if period_name == "D1" and cycle_data.get("current_price"):
            current_price = float(cycle_data["current_price"])
    result["current_price"] = current_price
    return result


# ============================================
# AI 提示词
# ============================================

def build_analysis_prompt(data: Dict[str, Any], independent: bool = False) -> str:
    """
    构建分析提示词

    Args:
        data: 缠论数据
        independent: 是否强调独立推理（委员模式）
    """
    extra = "\n请独立推理，不参考其他观点。" if independent else ""

    # 检查是否有持仓信息
    position_context = ""
    position = data.get("position")
    if position and position.get("type") != "NONE":
        pos_type = "做多" if position["type"] == "LONG" else "做空"
        current_price = data.get("current_price", 0)
        entry_price = position.get("entry_price", 0)

        # 计算盈亏比例
        if entry_price and current_price:
            if position["type"] == "LONG":
                pnl_pct = ((current_price / entry_price) - 1) * 100
            else:
                pnl_pct = ((entry_price / current_price) - 1) * 100
        else:
            pnl_pct = 0

        position_context = f"""

【当前持仓信息】
- 持仓方向：{pos_type}
- 开仓均价：{entry_price}
- 当前价格：{current_price}
- 浮动盈亏：{pnl_pct:.2f}%

请在分析时考虑当前持仓情况，给出持仓建议（持有、加仓、减仓、止盈、止损等）。
"""

    return f"""你是一名专业缠论交易分析员。

请基于以下缠论数据，给出交易策略。
{position_context}
你的分析应包含：方向判断、关键价位、风险点等，要求800字以内。
{extra}
多周期数据：
```json
{json.dumps(data, ensure_ascii=False, indent=2)}
```
"""


def build_judge_prompt(a: str, b: str, c: str, position: Dict = None) -> str:
    """
    构建裁决官提示词

    核心约束：裁决官不能重新分析原始市场数据，不看持仓信息，只能基于三份报告推理

    Args:
        a: 委员A 分析结果
        b: 委员B 分析结果
        c: 委员C 分析结果
        position: 持仓信息（不使用，裁决官不看持仓）
    """
    return f"""你是一名交易委员会裁决官。

以下是三名分析员的独立报告：

【分析A】
{a}

【分析B】
{b}

【分析C】
{c}

请基于这三份报告进行综合判断，给出交易策略，500字以内。

重要：
你不能重新分析市场原始数据，
只能基于三份报告进行推理。
"""


# ============================================
# AI 调用
# ============================================

def call_ai(prompt: str, api_key: str, model: str = None, temperature: float = 0.4, max_tokens: int = None) -> str:
    """
    调用 AI API

    Args:
        prompt: 提示词
        api_key: API 密钥
        model: 模型名称（默认使用 DEFAULT_MODEL）
        temperature: 温度参数
        max_tokens: 最大输出 tokens（None 表示使用模型默认值）
    """
    model = model or DEFAULT_MODEL
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是专业交易分析助手，请用中文回答。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"API 调用 ({model}, temp={temperature}, max_tokens={max_tokens}) 尝试 {attempt + 1}/{MAX_RETRIES}")
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            if content:
                return content
        except requests.exceptions.RequestException as e:
            logger.error(f"API 请求失败: {e}")
    return ""


# ============================================
# 三委员机制
# ============================================

def run_committee_analysis(data: Dict[str, Any], api_key: str) -> str:
    """
    运行三委员分析机制

    流程：
    1. 三委员并行/串行独立分析（各自使用不同温度）
    2. 裁决官基于三份报告进行二级推理
    3. 返回完整分析结果
    """
    config = COMMITTEE_CONFIG

    # 未启用三委员机制，使用单次调用
    if not config.get("enabled", False):
        logger.info("三委员机制未启用，使用单次调用")
        return call_ai(build_analysis_prompt(data), api_key)

    logger.info("启动三委员机制...")
    prompt = build_analysis_prompt(data, independent=True)
    analyses: List[str] = []

    # 获取各委员温度配置
    temperatures = config.get("committee_temperatures", [0.6, 0.6, 0.6])
    committee_count = config["committee_count"]
    committee_max_tokens = config.get("committee_max_tokens")

    # 并行/串行调用三委员
    if config.get("parallel", True):
        logger.info("并行调用三委员...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=committee_count) as executor:
            futures = [
                executor.submit(
                    call_ai, prompt, api_key,
                    config["committee_model"],
                    temperatures[i] if i < len(temperatures) else temperatures[-1],
                    committee_max_tokens
                )
                for i in range(committee_count)
            ]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=config.get("timeout", 120))
                    if result:
                        analyses.append(result)
                except Exception as e:
                    logger.warning(f"委员调用失败: {e}")
    else:
        logger.info("串行调用三委员...")
        for i in range(committee_count):
            temp = temperatures[i] if i < len(temperatures) else temperatures[-1]
            logger.info(f"  委员{chr(65 + i)} 温度={temp}")
            result = call_ai(
                prompt, api_key,
                config["committee_model"],
                temp,
                committee_max_tokens
            )
            if result:
                analyses.append(result)

    # 检查结果
    valid_analyses = [a for a in analyses if a]
    logger.info(f"委员分析完成: {len(valid_analyses)}/{config['committee_count']} 成功")

    # 失败降级
    if len(valid_analyses) < 2:
        if config.get("fallback_on_failure", True):
            logger.warning("委员分析失败过多，降级到单次调用")
            return call_ai(build_analysis_prompt(data), api_key)
        return "委员分析失败"

    # 补齐到3份
    while len(valid_analyses) < 3:
        valid_analyses.append(valid_analyses[0])

    # 裁决官分析
    logger.info("进入裁决阶段...")
    # 提取持仓信息，传递给裁决官
    position = data.get("position")
    final_decision = call_ai(
        build_judge_prompt(*valid_analyses[:3], position=position),
        api_key,
        config["judge_model"],
        config["judge_temperature"],
        config.get("judge_max_tokens")
    )

    if not final_decision:
        if config.get("fallback_on_failure", True):
            logger.warning("裁决失败，返回委员分析结果")
            return format_committee_result(valid_analyses[:3], None)
        return "裁决失败"

    return format_committee_result(valid_analyses[:3], final_decision)


def format_committee_result(analyses: List[str], final_decision: Optional[str]) -> str:
    """格式化三委员分析结果"""
    lines = [
        "\n" + "=" * 60,
        "三委员分析结果",
        "=" * 60,
    ]
    for i, analysis in enumerate(analyses):
        lines.append(f"\n【委员{chr(65 + i)}】")
        lines.append(analysis)

    if final_decision:
        lines.extend([
            "\n" + "=" * 60,
            "裁决官最终结论",
            "=" * 60,
            f"\n{final_decision}",
        ])
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


# ============================================
# 输出格式化
# ============================================

def parse_strategy_json(response_text: str) -> Optional[Dict[str, Any]]:
    """尝试从响应中解析 JSON"""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # 尝试提取代码块中的 JSON
    for match in re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text):
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    # 尝试提取花括号内容
    match = re.search(r"\{[\s\S]*\}", response_text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def format_strategy(raw_response: str) -> str:
    """格式化策略输出"""
    lines = ["=" * 60, "AI 策略输出", "=" * 60, ""]
    if raw_response.strip():
        lines.append(raw_response.strip())
    else:
        lines.append("AI 无有效输出")
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


# ============================================
# 主流程
# ============================================

def analyze_symbol(symbol: str, api_key: str, position: Optional[Dict[str, Any]] = None) -> None:
    """
    分析单个交易对

    Args:
        symbol: 交易对
        api_key: API 密钥
        position: 持仓信息（可选），格式: {"type": "LONG/SHORT", "entry_price": xxx}
    """
    print(f"\n{'='*60}")
    print(f"分析 {symbol}")
    if position:
        pos_type = "做多" if position["type"] == "LONG" else "做空"
        print(f"持仓: {pos_type} @ {position['entry_price']}")
    print("=" * 60)
    try:
        print("\n获取多周期缠论数据...")
        chanlun_data = get_multi_cycle_data(symbol)

        # 将持仓信息合并到缠论数据中
        if position:
            chanlun_data["position"] = position

        print("\n" + "=" * 60)
        print("缠论数据")
        print("=" * 60)
        for cycle_data in chanlun_data.get("cycles", {}).values():
            formatted = cycle_data.get("formatted_text", "")
            if formatted:
                print(formatted)

        # AI 分析
        print("\n发送缠论数据给 AI ...")
        if COMMITTEE_CONFIG.get("enabled", False):
            print(f"（三委员模式：{COMMITTEE_CONFIG['committee_count']}委员 + 1裁决官）")
        strategy_text = run_committee_analysis(chanlun_data, api_key)

        if strategy_text:
            print(format_strategy(strategy_text))
        else:
            print("AI 生成失败")

    except Exception as e:
        print(f"\n错误: {e}")
        logger.error(f"策略生成失败: {e}")


def main() -> None:
    """主入口"""
    print("\n" + "=" * 60)
    print("AI 策略引擎 - 缠论数据 → AI 策略")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not DEEPSEEK_API_KEY:
        print("\n错误: 未配置 DEEPSEEK_API_KEY")
        return

    if PROXY_URL:
        BinanceAPI.set_proxy(PROXY_URL)

    # 选择交易对
    symbols = select_symbol()

    # 选择持仓信息
    position = select_position()

    # 分析
    for symbol in symbols:
        analyze_symbol(symbol, DEEPSEEK_API_KEY, position=position)

    print("\n分析完成")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户取消")
        sys.exit(0)

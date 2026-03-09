"""
AI 分析模块 - 重构版（4层引擎架构 + 认知AI层）

架构：
市场数据 → StructureEngine → RiskEngine → DecisionEngine → ExplanationEngine → 报告
                                        ↓
                                  CognitiveAI (可选，认知增强)

改进：
1. 分层架构，职责明确
2. 每层可独立测试
3. 风控使用纯数学计算
4. 解释使用自然语言生成
5. AI只做认知增强，不改决策
"""

import re
import json
import logging
import time
import requests
from datetime import datetime
from typing import Tuple, Optional, Dict, Any

# 导入4层引擎
from engines.structure_engine import StructureEngine
from engines.risk_engine import RiskEngine
from engines.decision_engine import DecisionEngine
from engines.explanation_engine import ExplanationEngine

# 导入认知AI引擎
from engines.cognitive_ai import CognitiveAI, CognitiveInsight

# 导入数据模型
from models.state_models import (
    ChanData,
    Indicators,
    StructureState,
    RiskProfile,
    Decision,
    TradingPlan
)

# ============================================
# 常量配置
# ============================================
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_MODEL = "deepseek-reasoner"
MAX_RETRIES = 3
RETRY_DELAY = 2  # 秒
MIN_SYSTEM_SCORE = 6.5  # 最低系统评分阈值

# ============================================
# 日志配置
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_analysis.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def parse_chan_results(chan_results: str) -> ChanData:
    """
    解析缠论原始数据，提取结构化信息

    Args:
        chan_results: 缠论原始输出文本

    Returns:
        ChanData: 解析后的结构化数据
    """
    chan_data = ChanData()

    # 按周期分割
    sections = re.split(r'---+\n', chan_results)

    for section in sections:
        if not section.strip():
            continue

        # 判断周期
        if "日线" in section[:50]:
            cycle_data = _parse_cycle_section(section)
            chan_data.daily = cycle_data
        elif "4小时" in section[:50]:
            cycle_data = _parse_cycle_section(section)
            chan_data.h4 = cycle_data
        elif "1小时" in section[:50]:
            cycle_data = _parse_cycle_section(section)
            chan_data.h1 = cycle_data
        elif "15分钟" in section[:50]:
            cycle_data = _parse_cycle_section(section)
            chan_data.m15 = cycle_data

        # 提取当前价格
        if "收盘价:" in section:
            match = re.search(r'收盘价:\s*([\d.]+)', section)
            if match:
                chan_data.current_price = float(match.group(1))

    # 设置交易对
    if "BTCUSDT" in chan_results:
        chan_data.symbol = "BTCUSDT"
    elif "ETHUSDT" in chan_results:
        chan_data.symbol = "ETHUSDT"

    return chan_data


def _parse_cycle_section(section: str) -> Dict[str, Any]:
    """
    解析单个周期的数据

    Args:
        section: 单个周期的文本

    Returns:
        Dict: 解析后的周期数据
    """
    data = {}

    # 解析收盘价
    match = re.search(r'收盘价:\s*([\d.]+)', section)
    if match:
        data["close"] = float(match.group(1))

    # 解析MACD
    match = re.search(r'MACD:\s*(-?[\d.]+)', section)
    if match:
        data["macd_value"] = float(match.group(1))

    # 解析笔方向
    if "当前笔: 向上" in section:
        data["bi_direction"] = "向上"
    elif "当前笔: 向下" in section:
        data["bi_direction"] = "向下"
    else:
        data["bi_direction"] = "未知"

    # 解析线段方向
    if "当前线段: 向上" in section:
        data["segment_direction"] = "向上"
    elif "当前线段: 向下" in section:
        data["segment_direction"] = "向下"
    else:
        data["segment_direction"] = "未知"

    # 解析中枢位置
    if "中枢下方" in section:
        data["zs_position"] = "中枢下方（弱势）"
    elif "中枢上方" in section:
        data["zs_position"] = "中枢上方（强势）"
    elif "中枢下半部分" in section:
        data["zs_position"] = "中枢下半部分"
    elif "中枢上半部分" in section:
        data["zs_position"] = "中枢上半部分"
    elif "中枢内" in section:
        data["zs_position"] = "中枢内"
    else:
        data["zs_position"] = "未知"

    # 解析最近高点/低点（从笔分析中提取）
    bi_matches = re.findall(r'笔\d+:\s*[上下][向],\s*起点=([\d.]+),\s*终点=([\d.]+)', section)
    if bi_matches:
        highs = []
        lows = []
        for start, end in bi_matches:
            highs.append(max(float(start), float(end)))
            lows.append(min(float(start), float(end)))
        data["recent_high"] = max(highs) if highs else data.get("close", 0)
        data["recent_low"] = min(lows) if lows else data.get("close", 0)

    return data


def extract_indicators(chan_data: ChanData) -> Indicators:
    """
    从缠论数据中提取技术指标

    Args:
        chan_data: 缠论数据

    Returns:
        Indicators: 技术指标
    """
    indicators = Indicators()

    # 设置当前价格
    indicators.current_price = chan_data.current_price

    # 从各周期收集数据
    all_highs = []
    all_lows = []

    for cycle_data in [chan_data.daily, chan_data.h4, chan_data.h1, chan_data.m15]:
        if cycle_data:
            if cycle_data.get("recent_high"):
                all_highs.append(cycle_data["recent_high"])
            if cycle_data.get("recent_low"):
                all_lows.append(cycle_data["recent_low"])

    if all_highs:
        indicators.recent_high = max(all_highs)
    if all_lows:
        indicators.recent_low = min(all_lows)

    # 估算ATR（使用高低点差的20%）
    if indicators.recent_high > 0 and indicators.recent_low > 0:
        indicators.atr = (indicators.recent_high - indicators.recent_low) * 0.2
        if indicators.current_price > 0:
            indicators.atr_percent = indicators.atr / indicators.current_price

    # 估算波动率
    if indicators.atr_percent > 0:
        indicators.volatility = indicators.atr_percent

    return indicators


def run_engine_pipeline(chan_data: ChanData, indicators: Indicators) -> Tuple[StructureState, RiskProfile, Decision, TradingPlan]:
    """
    运行4层引擎管道

    Args:
        chan_data: 缠论数据
        indicators: 技术指标

    Returns:
        Tuple: (结构状态, 风控评估, 决策结果, 交易计划)
    """
    logger.info("开始运行4层引擎管道...")

    # 1. 结构推理引擎
    structure_engine = StructureEngine()
    structure = structure_engine.analyze(chan_data)
    logger.info(f"结构推理完成: {structure.dominant_cycle} {structure.trend} {structure.phase}")

    # 2. 风控评估引擎
    risk_engine = RiskEngine()
    risk = risk_engine.evaluate(structure, indicators)
    logger.info(f"风控评估完成: 风险等级={risk.risk_level}, 仓位={risk.position_hint}")

    # 3. 决策融合引擎
    decision_engine = DecisionEngine()
    decision = decision_engine.decide(structure, risk)
    logger.info(f"决策完成: {decision.action} (置信度={decision.confidence})")

    # 4. 生成交易计划
    trading_plan = decision_engine.generate_trading_plan(
        structure, risk, decision, chan_data.current_price
    )

    return structure, risk, decision, trading_plan


def apply_safety_rules(decision: Decision, structure: StructureState) -> Decision:
    """
    应用安全规则

    Args:
        decision: 决策结果
        structure: 结构状态

    Returns:
        Decision: 处理后的决策
    """
    should_wait = False
    reasons = []

    # 规则1：共振强度过低
    if decision.resonance_strength < 0.5 and decision.resonance_type != "趋势共振":
        should_wait = True
        reasons.append(f"共振强度过低({decision.resonance_strength*100:.0f}%)")

    # 规则2：置信度过低
    if decision.confidence < 0.5:
        should_wait = True
        reasons.append(f"置信度过低({decision.confidence:.2f})")

    # 规则3：系统评分过低
    if decision.system_score < MIN_SYSTEM_SCORE:
        should_wait = True
        reasons.append(f"系统评分过低({decision.system_score:.2f})")

    # 规则4：加权分数绝对值<2
    if structure.cycle_score and abs(structure.cycle_score.weighted_score) < 2:
        should_wait = True
        reasons.append(f"加权分数绝对值<2({structure.cycle_score.weighted_score})")

    if should_wait and decision.action != "WAIT":
        original_action = decision.action
        decision.action = "WAIT"
        logger.warning(f"安全规则触发，信号从 {original_action} 覆盖为 WAIT: {', '.join(reasons)}")

    return decision


def analyze_with_deepseek(
    chan_results: str,
    api_key: str,
    symbol: str = None,
    use_cognitive_ai: bool = True
) -> str:
    """
    主分析函数（协调器）

    流程:
    1. 解析缠论数据
    2. 提取技术指标
    3. 运行4层引擎管道
    4. 应用安全规则
    5. 生成解释报告
    6. (可选) AI认知增强

    Args:
        chan_results: 缠论原始输出
        api_key: DeepSeek API密钥
        symbol: 交易对（可选）
        use_cognitive_ai: 是否启用AI认知增强（默认True）

    Returns:
        str: 分析报告
    """
    logger.info("=" * 60)
    logger.info("开始分析...")

    try:
        # 1. 解析缠论数据
        chan_data = parse_chan_results(chan_results)
        if symbol:
            chan_data.symbol = symbol

        # 2. 提取技术指标
        indicators = extract_indicators(chan_data)

        # 3. 运行4层引擎管道
        structure, risk, decision, trading_plan = run_engine_pipeline(chan_data, indicators)

        # 4. 应用安全规则
        decision = apply_safety_rules(decision, structure)

        # 5. 生成解释报告
        explanation_engine = ExplanationEngine()
        report = explanation_engine.generate(structure, risk, decision, trading_plan)

        # 6. (可选) AI认知增强 - 不改决策，只提供认知洞察
        if use_cognitive_ai and api_key:
            logger.info("启用AI认知增强...")
            cognitive_ai = CognitiveAI(api_key=api_key)
            insight = cognitive_ai.analyze(
                structure=structure,
                risk=risk,
                decision=decision,
                trading_plan=trading_plan,
                current_price=chan_data.current_price,
                symbol=chan_data.symbol
            )

            if insight.success:
                # 将AI认知分析追加到报告
                cognitive_report = cognitive_ai.format_insight(insight)
                report = report + "\n\n" + cognitive_report
                logger.info("AI认知增强完成")
            else:
                logger.warning(f"AI认知增强失败: {insight.error}")

        logger.info(f"分析完成: {chan_data.symbol} - {decision.action}")
        logger.info("=" * 60)

        return report

    except Exception as e:
        logger.error(f"分析失败: {e}")
        return f"⚠️ 分析失败: {e}"


# ============================================
# 兼容旧版本的函数（保留向后兼容）
# ============================================

def build_prompt(chan_results: str, symbol: str = "BTCUSDT") -> str:
    """
    构建提示词（保留用于AI辅助）

    注意：新架构中，AI仅用于解释生成，不参与决策
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prompt = f"""
你是一名专业的缠论结构分析助手。

当前时间: {current_time}
交易对: {symbol}
缠论数据:
{chan_results}

请分析上述缠论数据，提供简洁的市场结构描述。
"""
    return prompt


def parse_ai_response(response_text: str) -> Optional[dict]:
    """
    解析AI响应，提取JSON（兼容旧版本）
    """
    try:
        # 尝试直接解析
        return json.loads(response_text)
    except json.JSONDecodeError:
        # 尝试提取JSON块
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, response_text)
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass

        # 尝试提取花括号内容
        brace_pattern = r'\{[\s\S]*\}'
        match = re.search(brace_pattern, response_text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

    return None


def validate_signal(data: dict, symbol: str = None) -> Tuple[bool, str]:
    """
    验证信号数据（兼容旧版本）
    """
    if not data:
        return False, "数据为空"

    # 检查必要字段
    if "action" not in data:
        return False, "缺少 action 字段"

    action = data.get("action")
    if action not in ["BUY", "SELL", "WAIT"]:
        return False, f"无效的 action: {action}"

    return True, "验证通过"


# ============================================
# 测试函数
# ============================================

def test_engines():
    """测试4层引擎"""
    # 创建测试数据
    chan_data = ChanData(
        symbol="BTCUSDT",
        current_price=67000,
        daily={
            "bi_direction": "向下",
            "segment_direction": "向上",
            "zs_position": "中枢下方（弱势）",
            "macd_value": 1413.98,
            "recent_high": 97924.49,
            "recent_low": 60000.00
        },
        h4={
            "bi_direction": "向上",
            "segment_direction": "向上",
            "zs_position": "中枢下半部分",
            "macd_value": 372.42,
            "recent_high": 69988.83,
            "recent_low": 62510.28
        },
        h1={
            "bi_direction": "向下",
            "segment_direction": "向下",
            "zs_position": "中枢下方（弱势）",
            "macd_value": -152.36,
            "recent_high": 69988.83,
            "recent_low": 66500.00
        },
        m15={
            "bi_direction": "向上",
            "segment_direction": "向上",
            "zs_position": "中枢下方（弱势）",
            "macd_value": -23.59,
            "recent_high": 67656.11,
            "recent_low": 66885.00
        }
    )

    indicators = extract_indicators(chan_data)

    # 运行管道
    structure, risk, decision, trading_plan = run_engine_pipeline(chan_data, indicators)

    # 生成报告
    explanation_engine = ExplanationEngine()
    report = explanation_engine.generate(structure, risk, decision, trading_plan)

    # 处理 Windows 控制台编码问题
    try:
        print(report)
    except UnicodeEncodeError:
        # 移除 emoji 后打印
        import sys
        sys.stdout.buffer.write(report.encode('utf-8', errors='replace'))

    return structure, risk, decision, trading_plan


if __name__ == "__main__":
    test_engines()

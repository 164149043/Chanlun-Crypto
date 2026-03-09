"""
数据模型定义 - 4层引擎架构

定义各引擎的输入输出数据结构
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any


@dataclass
class CycleScore:
    """多周期方向评分"""
    daily: int = 0          # -1, 0, 1
    h4: int = 0             # -1, 0, 1
    h1: int = 0             # -1, 0, 1
    m15: int = 0            # -1, 0, 1
    weighted_score: float = 0.0
    bias: str = "震荡"      # "偏多" | "偏空" | "震荡"


@dataclass
class KeyLevels:
    """关键价位"""
    resistance_zone: Dict[str, Any] = field(default_factory=dict)   # {high, low, strength}
    support_zone: Dict[str, Any] = field(default_factory=dict)      # {high, low, strength}
    breakout_confirm: str = ""      # 突破确认描述
    breakdown_confirm: str = ""     # 跌破确认描述


@dataclass
class SignalQuality:
    """信号质量"""
    type: str = "无"           # "买点" | "卖点" | "无"
    strength: str = "弱"       # "强" | "中" | "弱" | "失败"
    has_edge: bool = False
    reason: str = ""


@dataclass
class StructureState:
    """
    结构推理结果

    由 StructureEngine 输出
    描述市场当前的结构状态
    """
    # 主导周期
    dominant_cycle: str = "日线"     # "日线" | "4小时" | "1小时" | "15分钟"
    dominant_cycle_reason: str = ""   # 主导周期选择理由

    # 趋势方向
    trend: str = "sideways"           # "bullish" | "bearish" | "sideways"

    # 市场阶段（状态机）
    phase: str = "range"              # "trend_start" | "trend_extend" | "rebound" | "range" | "exhaustion"

    # 阶段位置
    position: str = "中段"            # "初段" | "中段" | "末段"

    # 趋势类型
    trend_type: str = ""              # "主升" | "反弹" | "回调" | "下跌延续"

    # 结构强度 (0.0 - 1.0)
    strength: float = 0.5

    # 结构证据
    evidence: Dict[str, str] = field(default_factory=dict)   # {bi, segment, zs, macd}

    # 阶段转换预警
    transition_warning: str = ""

    # 多周期方向评分
    cycle_score: Optional[CycleScore] = None

    # 关键价位
    key_levels: Optional[KeyLevels] = None


@dataclass
class RiskProfile:
    """
    风控评估结果

    由 RiskEngine 输出
    纯数学计算，不使用AI
    """
    # 风险等级
    risk_level: str = "medium"        # "low" | "medium" | "high"

    # ATR波动率
    atr: float = 0.0
    atr_percent: float = 0.0          # ATR占价格百分比

    # 风险收益比
    reward_ratio: float = 2.0

    # 止损价位
    stop_loss_long: float = 0.0       # 做多止损
    stop_loss_short: float = 0.0      # 做空止损

    # 止损区间
    stop_zone_long: Dict[str, float] = field(default_factory=dict)   # {high, low}
    stop_zone_short: Dict[str, float] = field(default_factory=dict)  # {high, low}

    # 建议仓位比例 (0.0 - 1.0)
    position_size: float = 0.25       # 保守25%

    # 仓位描述
    position_hint: str = "保守(25%)"  # "保守(25%)" | "标准(50%)" | "激进(75%)"


@dataclass
class Decision:
    """
    决策结果

    由 DecisionEngine 输出
    综合结构和风控做出决策
    """
    # 操作动作
    action: str = "WAIT"              # "BUY" | "SELL" | "WAIT"

    # 置信度 (0.0 - 1.0)
    confidence: float = 0.5

    # 入场时机
    entry_hint: str = "观望等待"       # "回调入场" | "突破入场" | "反弹入场" | "回调阻力" | "观望等待"

    # 概率偏向
    probability_bias: str = "中"       # "高" | "中" | "低"

    # 多空概率
    bullish_prob: float = 0.35
    bearish_prob: float = 0.35
    sideways_prob: float = 0.30

    # 置信度描述
    confidence_level: str = "中"       # "高" | "中" | "低"

    # 决策理由
    reason: str = ""

    # 共振分析
    resonance: bool = False
    resonance_strength: float = 0.0
    resonance_type: str = ""           # "强共振" | "趋势共振" | "无共振"

    # 系统评分 (0-10)
    system_score: float = 0.0

    # 一句话结论
    summary: str = ""


@dataclass
class TradingPlan:
    """
    交易计划

    包含做多、做空、震荡三种情况的推演
    """
    # 做多推演
    long_scenario: Dict[str, Any] = field(default_factory=lambda: {
        "trigger": "",
        "target_zone": {"high": 0, "low": 0},
        "logic": "",
        "reason": ""
    })

    # 做空推演
    short_scenario: Dict[str, Any] = field(default_factory=lambda: {
        "trigger": "",
        "target_zone": {"high": 0, "low": 0},
        "logic": "",
        "reason": ""
    })

    # 震荡推演
    sideways_scenario: Dict[str, Any] = field(default_factory=lambda: {
        "range": {"high": 0, "low": 0},
        "logic": "",
        "reason": ""
    })


@dataclass
class ChanData:
    """
    缠论解析数据

    从缠论原始输出中提取的结构化数据
    """
    # 交易对
    symbol: str = ""

    # 各周期数据
    daily: Dict[str, Any] = field(default_factory=dict)
    h4: Dict[str, Any] = field(default_factory=dict)
    h1: Dict[str, Any] = field(default_factory=dict)
    m15: Dict[str, Any] = field(default_factory=dict)

    # 当前价格
    current_price: float = 0.0


@dataclass
class Indicators:
    """
    技术指标数据

    用于风控计算
    """
    # ATR
    atr: float = 0.0
    atr_percent: float = 0.0

    # 波动率
    volatility: float = 0.0

    # 中枢距离
    zs_distance: float = 0.0

    # 当前价格
    current_price: float = 0.0

    # 最高价/最低价（用于止损计算）
    recent_high: float = 0.0
    recent_low: float = 0.0

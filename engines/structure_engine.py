"""
结构推理引擎 (Structure Engine)

职责：理解市场结构，判断趋势、周期、阶段
⚠️ 这一层不做交易决定，只理解结构

核心原则：
1. 大级别优先 - 日线趋势优先级高于4H/1H
2. 趋势主导周期 ≠ 动能活跃周期
3. 日线↓ + 4H↑ = "下跌趋势中的反弹"（非上涨趋势）
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple

from models.state_models import (
    StructureState,
    CycleScore,
    KeyLevels,
    ChanData
)

logger = logging.getLogger(__name__)


class StructureEngine:
    """
    结构推理引擎 - 理解市场发生了什么

    输入: 缠论原始数据（多周期K线、笔、线段、中枢、MACD）
    输出: StructureState
    """

    # 周期权重（用于加权评分）
    CYCLE_WEIGHTS = {
        "日线": 3.0,
        "4小时": 2.0,
        "1小时": 1.5,
        "15分钟": 1.0,
    }

    def __init__(self):
        pass

    def analyze(self, chan_data: ChanData) -> StructureState:
        """
        分析缠论数据，判断结构状态

        Args:
            chan_data: 解析后的缠论数据

        Returns:
            StructureState: 结构推理结果
        """
        logger.info("开始结构推理分析...")

        # 1. 判断主导周期（大级别优先原则）
        dominant_cycle, dominant_reason = self._determine_dominant_cycle(chan_data)

        # 2. 判断趋势方向
        trend = self._determine_trend(chan_data, dominant_cycle)

        # 3. 判断市场阶段（状态机）
        phase, position = self._determine_phase(chan_data, trend, dominant_cycle)

        # 4. 判断趋势类型
        trend_type = self._determine_trend_type(chan_data, trend, dominant_cycle)

        # 5. 计算结构强度
        strength = self._calculate_strength(chan_data, trend)

        # 6. 收集证据
        evidence = self._collect_evidence(chan_data)

        # 7. 计算多周期方向评分
        cycle_score = self._calculate_cycle_score(chan_data)

        # 8. 确定关键价位
        key_levels = self._determine_key_levels(chan_data)

        # 9. 生成阶段转换预警
        transition_warning = self._generate_transition_warning(
            chan_data, trend, phase, cycle_score
        )

        state = StructureState(
            dominant_cycle=dominant_cycle,
            dominant_cycle_reason=dominant_reason,
            trend=trend,
            phase=phase,
            position=position,
            trend_type=trend_type,
            strength=strength,
            evidence=evidence,
            transition_warning=transition_warning,
            cycle_score=cycle_score,
            key_levels=key_levels,
        )

        logger.info(f"结构推理完成: {dominant_cycle} {trend} {phase}")
        return state

    def _determine_dominant_cycle(self, chan_data: ChanData) -> Tuple[str, str]:
        """
        判断主导周期（大级别优先原则）

        规则：
        1. 如果日线趋势明确（笔方向一致+价格在中枢外），主导周期=日线
        2. 如果日线震荡（价格在中枢内），看4H是否形成突破
        3. 不能因为4H动能强就把4H定为主导周期

        Returns:
            (周期名称, 选择理由)
        """
        daily = chan_data.daily
        h4 = chan_data.h4

        # 检查日线趋势是否明确
        daily_trend_clear = self._is_trend_clear(daily)

        if daily_trend_clear:
            reason = "日线趋势明确（笔方向一致，价格在中枢外），决定大方向"
            return "日线", reason

        # 日线震荡，检查4H
        h4_trend_clear = self._is_trend_clear(h4)
        if h4_trend_clear:
            reason = "日线震荡，4H形成明确趋势"
            return "4小时", reason

        # 默认使用日线
        reason = "日线决定大方向，即使当前处于震荡"
        return "日线", reason

    def _is_trend_clear(self, cycle_data: Dict) -> bool:
        """判断周期趋势是否明确"""
        if not cycle_data:
            return False

        # 检查笔方向
        bi_dir = cycle_data.get("bi_direction", "")
        # 检查价格相对中枢位置
        zs_position = cycle_data.get("zs_position", "")

        # 趋势明确 = 笔方向一致 + 价格在中枢外
        if bi_dir in ["向上", "向下"] and "中枢" in zs_position:
            if "下方" in zs_position or "上方" in zs_position:
                return True

        return False

    def _determine_trend(self, chan_data: ChanData, dominant_cycle: str) -> str:
        """
        判断趋势方向

        规则：
        - 大级别趋势优先级永远高于小级别
        - 日线下跌趋势中，4H上涨只能定性为"反弹"
        """
        # 获取主导周期数据
        if dominant_cycle == "日线":
            main_data = chan_data.daily
        elif dominant_cycle == "4小时":
            main_data = chan_data.h4
        else:
            main_data = chan_data.daily

        if not main_data:
            return "sideways"

        # 判断趋势
        bi_dir = main_data.get("bi_direction", "")
        zs_position = main_data.get("zs_position", "")

        if bi_dir == "向上" and "上方" in zs_position:
            return "bullish"
        elif bi_dir == "向下" and "下方" in zs_position:
            return "bearish"
        else:
            return "sideways"

    def _determine_phase(
        self, chan_data: ChanData, trend: str, dominant_cycle: str
    ) -> Tuple[str, str]:
        """
        判断市场阶段（状态机）

        阶段定义：
        - trend_start: 趋势启动，刚形成，动量初现
        - trend_extend: 趋势延续，动量稳定
        - rebound: 反弹/回调
        - range: 震荡整理
        - exhaustion: 末端衰竭，内部结构破坏

        Returns:
            (阶段, 位置)
        """
        daily = chan_data.daily
        h4 = chan_data.h4
        h1 = chan_data.h1

        # 获取日线和4H的笔方向
        daily_bi = daily.get("bi_direction", "") if daily else ""
        h4_bi = h4.get("bi_direction", "") if h4 else ""
        h1_bi = h1.get("bi_direction", "") if h1 else ""

        # 获取MACD状态
        daily_macd = daily.get("macd_value", 0) if daily else 0
        h4_macd = h4.get("macd_value", 0) if h4 else 0

        # 状态机逻辑
        if trend == "sideways":
            return "range", "中段"

        # 日线下跌 + 4H上涨 = 反弹
        if daily_bi == "向下" and h4_bi == "向上":
            # 判断反弹阶段
            if h4_macd > 0 and h1_bi == "向下":
                return "exhaustion", "末段"  # 反弹末段
            elif h4_macd > 0:
                return "rebound", "中段"  # 反弹中段
            else:
                return "rebound", "初段"  # 反弹初段

        # 日线上涨 + 4H下跌 = 回调
        if daily_bi == "向上" and h4_bi == "向下":
            if h4_macd < 0 and h1_bi == "向上":
                return "exhaustion", "末段"  # 回调末段
            elif h4_macd < 0:
                return "rebound", "中段"  # 回调中段
            else:
                return "rebound", "初段"  # 回调初段

        # 趋势延续
        if daily_bi == h4_bi:
            # 判断是否衰竭
            if abs(h4_macd) < abs(daily_macd) * 0.5:
                return "exhaustion", "末段"
            else:
                return "trend_extend", "中段"

        # 默认
        return "range", "中段"

    def _determine_trend_type(
        self, chan_data: ChanData, trend: str, dominant_cycle: str
    ) -> str:
        """
        判断趋势类型

        类型：
        - 主升: 上涨趋势延续
        - 反弹: 下跌趋势中的上涨
        - 回调: 上涨趋势中的下跌
        - 下跌延续: 下跌趋势延续
        """
        daily = chan_data.daily
        h4 = chan_data.h4

        daily_bi = daily.get("bi_direction", "") if daily else ""
        h4_bi = h4.get("bi_direction", "") if h4 else ""

        if trend == "bullish":
            if daily_bi == "向上":
                return "主升"
            else:
                return "反弹"
        elif trend == "bearish":
            if daily_bi == "向下":
                return "下跌延续"
            else:
                return "回调"
        else:
            return ""

    def _calculate_strength(self, chan_data: ChanData, trend: str) -> float:
        """
        计算结构强度 (0.0 - 1.0)

        考虑因素：
        1. 多周期方向一致性
        2. MACD强度
        3. 中枢位置
        """
        if trend == "sideways":
            return 0.3

        # 计算方向一致性得分
        directions = []
        for cycle_data in [chan_data.daily, chan_data.h4, chan_data.h1, chan_data.m15]:
            if cycle_data:
                bi_dir = cycle_data.get("bi_direction", "")
                if bi_dir == "向上":
                    directions.append(1)
                elif bi_dir == "向下":
                    directions.append(-1)
                else:
                    directions.append(0)

        # 一致性得分
        if directions:
            consistency = abs(sum(directions)) / len(directions)
        else:
            consistency = 0.5

        # MACD强度
        macd_scores = []
        for cycle_data in [chan_data.daily, chan_data.h4]:
            if cycle_data:
                macd = abs(cycle_data.get("macd_value", 0))
                macd_scores.append(min(macd / 1000, 1.0))  # 归一化

        macd_strength = sum(macd_scores) / len(macd_scores) if macd_scores else 0.5

        # 综合强度
        strength = consistency * 0.6 + macd_strength * 0.4

        return round(min(max(strength, 0.0), 1.0), 2)

    def _collect_evidence(self, chan_data: ChanData) -> Dict[str, str]:
        """
        收集结构证据

        Returns:
            {bi: 笔状态, segment: 线段状态, zs: 中枢状态, macd: MACD状态}
        """
        daily = chan_data.daily
        h4 = chan_data.h4
        h1 = chan_data.h1
        m15 = chan_data.m15

        evidence = {}

        # 笔状态
        bi_parts = []
        for name, data in [("日线", daily), ("4H", h4), ("1H", h1), ("15M", m15)]:
            if data:
                bi_dir = data.get("bi_direction", "未知")
                bi_parts.append(f"{name}笔{bi_dir}")
        evidence["bi"] = "，".join(bi_parts) if bi_parts else "无数据"

        # 线段状态
        seg_parts = []
        for name, data in [("日线", daily), ("4H", h4), ("1H", h1), ("15M", m15)]:
            if data:
                seg_dir = data.get("segment_direction", "未知")
                seg_parts.append(f"{name}线段{seg_dir}")
        evidence["segment"] = "，".join(seg_parts) if seg_parts else "无数据"

        # 中枢状态
        zs_parts = []
        for name, data in [("日线", daily), ("4H", h4), ("1H", h1), ("15M", m15)]:
            if data:
                zs_pos = data.get("zs_position", "未知")
                zs_parts.append(f"{name}{zs_pos}")
        evidence["zs"] = "，".join(zs_parts) if zs_parts else "无数据"

        # MACD状态
        macd_parts = []
        for name, data in [("日线", daily), ("4H", h4), ("1H", h1), ("15M", m15)]:
            if data:
                macd = data.get("macd_value", 0)
                macd_sign = "正" if macd >= 0 else "负"
                macd_parts.append(f"{name}MACD{macd_sign}")
        evidence["macd"] = "，".join(macd_parts) if macd_parts else "无数据"

        return evidence

    def _calculate_cycle_score(self, chan_data: ChanData) -> CycleScore:
        """
        计算多周期方向评分

        评分标准：
        - 明确上涨趋势 = +1
        - 明确下跌趋势 = -1
        - 震荡/矛盾 = 0

        权重：
        - 日线 ×3
        - 4H ×2
        - 1H ×1.5
        - 15M ×1
        """
        def get_direction(data: Dict) -> int:
            if not data:
                return 0
            bi_dir = data.get("bi_direction", "")
            macd = data.get("macd_value", 0)

            if bi_dir == "向上" and macd > 0:
                return 1
            elif bi_dir == "向下" and macd < 0:
                return -1
            elif bi_dir == "向上":
                return 1
            elif bi_dir == "向下":
                return -1
            else:
                return 0

        daily = get_direction(chan_data.daily)
        h4 = get_direction(chan_data.h4)
        h1 = get_direction(chan_data.h1)
        m15 = get_direction(chan_data.m15)

        # 加权分数
        weighted_score = (
            daily * self.CYCLE_WEIGHTS["日线"] +
            h4 * self.CYCLE_WEIGHTS["4小时"] +
            h1 * self.CYCLE_WEIGHTS["1小时"] +
            m15 * self.CYCLE_WEIGHTS["15分钟"]
        )

        # 判断偏向
        if weighted_score > 2:
            bias = "偏多"
        elif weighted_score < -2:
            bias = "偏空"
        else:
            bias = "震荡"

        return CycleScore(
            daily=daily,
            h4=h4,
            h1=h1,
            m15=m15,
            weighted_score=round(weighted_score, 2),
            bias=bias
        )

    def _determine_key_levels(self, chan_data: ChanData) -> KeyLevels:
        """
        确定关键价位

        规则：
        - 阻力区 = 最近结构高点附近 ± 0.5%
        - 支撑区 = 最近结构低点附近 ± 0.5%
        """
        current_price = chan_data.current_price

        # 收集各周期的高低点
        highs = []
        lows = []

        for cycle_data in [chan_data.daily, chan_data.h4, chan_data.h1]:
            if cycle_data:
                if cycle_data.get("recent_high"):
                    highs.append(cycle_data["recent_high"])
                if cycle_data.get("recent_low"):
                    lows.append(cycle_data["recent_low"])

        # 默认使用当前价格的±5%
        if not highs:
            highs = [current_price * 1.05]
        if not lows:
            lows = [current_price * 0.95]

        # 计算阻力区（最近高点）
        recent_high = max(highs)
        resistance_high = recent_high * 1.005  # +0.5%
        resistance_low = recent_high * 0.995   # -0.5%

        # 计算支撑区（最近低点）
        recent_low = min(lows)
        support_high = recent_low * 1.005
        support_low = recent_low * 0.995

        # 判断强度
        resistance_strength = "中"
        support_strength = "中"

        return KeyLevels(
            resistance_zone={
                "high": round(resistance_high, 2),
                "low": round(resistance_low, 2),
                "strength": resistance_strength
            },
            support_zone={
                "high": round(support_high, 2),
                "low": round(support_low, 2),
                "strength": support_strength
            },
            breakout_confirm=f"突破{round(resistance_high, 0):.0f}确认",
            breakdown_confirm=f"跌破{round(support_low, 0):.0f}确认"
        )

    def _generate_transition_warning(
        self,
        chan_data: ChanData,
        trend: str,
        phase: str,
        cycle_score: CycleScore
    ) -> str:
        """
        生成阶段转换预警

        在末段或出现背离时给出预警
        """
        warnings = []

        # 末段预警
        if phase == "exhaustion":
            if trend == "bearish":
                warnings.append("反弹末段，可能转折下跌")
            else:
                warnings.append("回调末段，可能转折上涨")

        # 方向冲突预警
        if cycle_score:
            positive = sum(1 for v in [cycle_score.daily, cycle_score.h4, cycle_score.h1, cycle_score.m15] if v > 0)
            negative = sum(1 for v in [cycle_score.daily, cycle_score.h4, cycle_score.h1, cycle_score.m15] if v < 0)

            if positive >= 2 and negative >= 2:
                warnings.append("多周期方向矛盾，等待确认")

        # MACD背离预警
        h4 = chan_data.h4
        h1 = chan_data.h1
        if h4 and h1:
            h4_macd = h4.get("macd_value", 0)
            h1_macd = h1.get("macd_value", 0)
            h4_bi = h4.get("bi_direction", "")
            h1_bi = h1.get("bi_direction", "")

            if h4_bi == "向上" and h4_macd > 0 and h1_macd < 0:
                warnings.append("4H上涨但1H MACD负，动能减弱")
            elif h4_bi == "向下" and h4_macd < 0 and h1_macd > 0:
                warnings.append("4H下跌但1H MACD正，可能反弹")

        return "；".join(warnings) if warnings else ""

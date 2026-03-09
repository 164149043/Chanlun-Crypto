"""
决策融合引擎 (Decision Engine)

职责：综合结构和风控做出交易决策
⚠️ 使用规则+概率，不使用AI

决策内容：
- 操作动作（BUY/SELL/WAIT）
- 多空概率
- 入场时机
- 置信度
- 共振分析
"""

import logging
from typing import Dict, Any, Optional

from models.state_models import (
    StructureState,
    RiskProfile,
    Decision,
    TradingPlan,
    CycleScore
)

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    决策融合引擎 - 综合结构和风控做出决策

    输入:
      - structure: 结构推理结果
      - risk: 风控评估结果
    输出: Decision
    """

    # 决策阈值
    WAIT_THRESHOLD = 2.0           # 加权分数绝对值<2时WAIT
    MIN_CONFIDENCE = 0.6           # 最小置信度
    MIN_RESonANCE_STRENGTH = 0.5   # 最小共振强度

    # 概率阈值
    HIGH_PROB_THRESHOLD = 0.65     # 高概率阈值
    LOW_PROB_THRESHOLD = 0.35      # 低概率阈值

    def __init__(self):
        pass

    def decide(self, structure: StructureState, risk: RiskProfile) -> Decision:
        """
        基于结构和风控做出交易决策

        Args:
            structure: 结构推理结果
            risk: 风控评估结果

        Returns:
            Decision: 决策结果
        """
        logger.info("开始决策融合...")

        # 1. 计算多空概率
        probability = self._calculate_probability(structure, risk)

        # 2. 分析共振
        resonance, resonance_strength, resonance_type = self._analyze_resonance(structure)

        # 3. 确定操作动作
        action = self._determine_action(structure, risk, probability, resonance)

        # 4. 确定入场时机
        entry_hint = self._determine_entry_hint(structure, action)

        # 5. 计算置信度
        confidence = self._calculate_confidence(structure, risk, probability, resonance)

        # 6. 确定概率偏向
        probability_bias = self._determine_probability_bias(probability)

        # 7. 确定置信度等级
        confidence_level = self._determine_confidence_level(confidence)

        # 8. 生成决策理由
        reason = self._generate_reason(structure, risk, action)

        # 9. 计算系统评分
        system_score = self._calculate_system_score(
            structure, risk, confidence, resonance, resonance_strength
        )

        # 10. 生成一句话结论
        summary = self._generate_summary(structure, action, probability)

        decision = Decision(
            action=action,
            confidence=confidence,
            entry_hint=entry_hint,
            probability_bias=probability_bias,
            bullish_prob=probability["bullish"],
            bearish_prob=probability["bearish"],
            sideways_prob=probability["sideways"],
            confidence_level=confidence_level,
            reason=reason,
            resonance=resonance,
            resonance_strength=resonance_strength,
            resonance_type=resonance_type,
            system_score=system_score,
            summary=summary
        )

        logger.info(f"决策完成: {action} (置信度={confidence:.2f}, 评分={system_score:.2f})")
        return decision

    def _calculate_probability(
        self,
        structure: StructureState,
        risk: RiskProfile
    ) -> Dict[str, float]:
        """
        计算多空概率

        基于加权分数和结构定性
        """
        cycle_score = structure.cycle_score
        if not cycle_score:
            return {"bullish": 0.35, "bearish": 0.35, "sideways": 0.30}

        weighted_score = cycle_score.weighted_score
        bias = cycle_score.bias

        # 基础概率
        if bias == "偏多":
            bullish_base = 0.55
            bearish_base = 0.25
            sideways_base = 0.20
        elif bias == "偏空":
            bullish_base = 0.25
            bearish_base = 0.55
            sideways_base = 0.20
        else:
            bullish_base = 0.35
            bearish_base = 0.35
            sideways_base = 0.30

        # 根据加权分数调整
        if weighted_score > 2:
            bullish_adj = min(weighted_score / 10, 0.15)
            bullish_base += bullish_adj
            bearish_base -= bullish_adj * 0.5
            sideways_base -= bullish_adj * 0.5
        elif weighted_score < -2:
            bearish_adj = min(abs(weighted_score) / 10, 0.15)
            bearish_base += bearish_adj
            bullish_base -= bearish_adj * 0.5
            sideways_base -= bearish_adj * 0.5

        # 根据结构阶段调整
        if structure.phase == "exhaustion":
            # 末段增加震荡概率
            sideways_base += 0.1
            if structure.trend == "bearish":
                bullish_base -= 0.05
            else:
                bearish_base -= 0.05

        # 确保概率在合理范围
        bullish = max(0.1, min(0.8, bullish_base))
        bearish = max(0.1, min(0.8, bearish_base))
        sideways = max(0.05, min(0.4, sideways_base))

        # 归一化
        total = bullish + bearish + sideways
        return {
            "bullish": round(bullish / total, 2),
            "bearish": round(bearish / total, 2),
            "sideways": round(sideways / total, 2)
        }

    def _analyze_resonance(
        self,
        structure: StructureState
    ) -> tuple:
        """
        分析共振

        Returns:
            (resonance: bool, strength: float, type: str)
        """
        cycle_score = structure.cycle_score
        if not cycle_score:
            return False, 0.0, "无共振"

        daily = cycle_score.daily
        h4 = cycle_score.h4
        h1 = cycle_score.h1
        m15 = cycle_score.m15

        # 统计方向数量
        positive_count = sum(1 for v in [daily, h4, h1, m15] if v > 0)
        negative_count = sum(1 for v in [daily, h4, h1, m15] if v < 0)

        # 计算共振强度
        max_aligned = max(positive_count, negative_count)
        resonance_strength = max_aligned / 4.0

        # 强共振：≥3周期方向一致
        if max_aligned >= 3:
            return True, round(resonance_strength, 2), "强共振"

        # 趋势共振：日线方向明确 + 至少2个周期与日线相同
        if daily != 0:
            same_as_daily = sum(1 for v in [daily, h4, h1, m15] if v == daily)
            if same_as_daily >= 2:
                return True, round(resonance_strength, 2), "趋势共振"

        # 无共振
        return False, round(resonance_strength, 2), "无共振"

    def _determine_action(
        self,
        structure: StructureState,
        risk: RiskProfile,
        probability: Dict[str, float],
        resonance: bool
    ) -> str:
        """
        确定操作动作

        规则：
        1. 加权分数绝对值<2时优先WAIT
        2. 需要共振或高概率才能BUY/SELL
        3. 考虑结构阶段
        """
        cycle_score = structure.cycle_score
        if not cycle_score:
            return "WAIT"

        weighted_score = cycle_score.weighted_score
        bias = cycle_score.bias

        # 规则1：加权分数绝对值<2时优先WAIT
        if abs(weighted_score) < self.WAIT_THRESHOLD:
            return "WAIT"

        # 规则2：末段阶段优先WAIT
        if structure.phase == "exhaustion":
            return "WAIT"

        # 规则3：无共振时优先WAIT
        if not resonance:
            return "WAIT"

        # 规则4：风险等级过高时优先WAIT
        if risk.risk_level == "high":
            return "WAIT"

        # 根据偏向确定动作
        if bias == "偏多" and probability["bullish"] >= self.HIGH_PROB_THRESHOLD:
            return "BUY"
        elif bias == "偏空" and probability["bearish"] >= self.HIGH_PROB_THRESHOLD:
            return "SELL"
        else:
            return "WAIT"

    def _determine_entry_hint(self, structure: StructureState, action: str) -> str:
        """
        确定入场时机

        规则：
        - BUY: 回调入场 或 突破入场
        - SELL: 反弹入场 或 回调阻力
        - WAIT: 观望等待
        """
        if action == "WAIT":
            return "观望等待"

        # 判断是趋势延续还是反转
        if structure.phase == "rebound":
            # 反弹/回调中
            if action == "BUY":
                return "回调入场"
            else:
                return "反弹入场"
        elif structure.phase == "trend_extend":
            # 趋势延续
            if action == "BUY":
                return "突破入场"
            else:
                return "回调阻力"
        else:
            if action == "BUY":
                return "回调入场"
            else:
                return "反弹入场"

    def _calculate_confidence(
        self,
        structure: StructureState,
        risk: RiskProfile,
        probability: Dict[str, float],
        resonance: bool
    ) -> float:
        """
        计算置信度 (0.0 - 1.0)

        考虑因素：
        1. 结构强度
        2. 共振
        3. 概率偏向程度
        4. 风险等级
        """
        # 基础置信度
        base_confidence = 0.5

        # 结构强度贡献
        strength_contribution = structure.strength * 0.2

        # 共振贡献
        resonance_contribution = 0.15 if resonance else 0

        # 概率偏向贡献
        max_prob = max(probability["bullish"], probability["bearish"])
        prob_contribution = (max_prob - 0.5) * 0.3 if max_prob > 0.5 else 0

        # 风险等级贡献
        if risk.risk_level == "low":
            risk_contribution = 0.1
        elif risk.risk_level == "high":
            risk_contribution = -0.1
        else:
            risk_contribution = 0

        # 综合置信度
        confidence = base_confidence + strength_contribution + resonance_contribution + prob_contribution + risk_contribution

        # 限制范围
        return round(max(0.3, min(0.95, confidence)), 2)

    def _determine_probability_bias(self, probability: Dict[str, float]) -> str:
        """确定概率偏向"""
        bullish = probability["bullish"]
        bearish = probability["bearish"]

        if bullish >= self.HIGH_PROB_THRESHOLD:
            return "高"
        elif bearish >= self.HIGH_PROB_THRESHOLD:
            return "高"
        elif bullish >= 0.5 or bearish >= 0.5:
            return "中"
        else:
            return "低"

    def _determine_confidence_level(self, confidence: float) -> str:
        """确定置信度等级"""
        if confidence >= 0.75:
            return "高"
        elif confidence >= 0.55:
            return "中"
        else:
            return "低"

    def _generate_reason(
        self,
        structure: StructureState,
        risk: RiskProfile,
        action: str
    ) -> str:
        """生成决策理由"""
        parts = []

        # 趋势方向
        trend_map = {"bullish": "上涨", "bearish": "下跌", "sideways": "震荡"}
        parts.append(f"趋势{trend_map.get(structure.trend, '不明')}")

        # 市场阶段
        phase_map = {
            "trend_start": "趋势启动",
            "trend_extend": "趋势延续",
            "rebound": "反弹/回调",
            "range": "震荡整理",
            "exhaustion": "末段衰竭"
        }
        parts.append(phase_map.get(structure.phase, "阶段不明"))

        # 共振状态
        if structure.cycle_score:
            parts.append(f"{structure.cycle_score.bias}")

        # 决策结果
        if action == "WAIT":
            parts.append("建议观望")
        elif action == "BUY":
            parts.append("偏多")
        else:
            parts.append("偏空")

        return "，".join(parts)

    def _calculate_system_score(
        self,
        structure: StructureState,
        risk: RiskProfile,
        confidence: float,
        resonance: bool,
        resonance_strength: float
    ) -> float:
        """
        计算系统评分 (0-10)

        公式：
        score = 0.35 * weighted_score_norm + 0.25 * resonance_score + 0.2 * strength_score + 0.2 * edge_bonus
        """
        # 加权分数归一化 (范围 -7.5 到 7.5)
        if structure.cycle_score:
            weighted_score = structure.cycle_score.weighted_score
            weighted_score_norm = (weighted_score + 7.5) / 15 * 10  # 0-10
        else:
            weighted_score_norm = 5.0

        # 共振评分
        resonance_score = resonance_strength * 10

        # 结构强度评分
        strength_score = structure.strength * 10

        # 交易优势加分
        edge_bonus = 10 if resonance and confidence >= 0.6 else 0

        # 综合评分
        score = (
            0.35 * weighted_score_norm +
            0.25 * resonance_score +
            0.2 * strength_score +
            0.2 * edge_bonus
        )

        return round(max(0, min(10, score)), 2)

    def _generate_summary(
        self,
        structure: StructureState,
        action: str,
        probability: Dict[str, float]
    ) -> str:
        """生成一句话结论"""
        # 趋势描述
        trend_desc = {
            "bullish": "上涨趋势",
            "bearish": "下跌趋势",
            "sideways": "震荡"
        }.get(structure.trend, "不明")

        # 阶段描述
        phase_desc = {
            "trend_start": "启动",
            "trend_extend": "延续",
            "rebound": "反弹/回调",
            "range": "震荡",
            "exhaustion": "末段"
        }.get(structure.phase, "")

        # 动作描述
        action_desc = {
            "BUY": "偏多概率高",
            "SELL": "偏空概率高",
            "WAIT": "建议观望"
        }.get(action, "")

        # 概率信息
        max_prob = max(probability["bullish"], probability["bearish"])
        if probability["bullish"] > probability["bearish"]:
            prob_desc = f"多头{max_prob*100:.0f}%"
        else:
            prob_desc = f"空头{max_prob*100:.0f}%"

        return f"{structure.dominant_cycle}{trend_desc}{phase_desc}，{prob_desc}，{action_desc}"

    def generate_trading_plan(
        self,
        structure: StructureState,
        risk: RiskProfile,
        decision: Decision,
        current_price: float
    ) -> TradingPlan:
        """
        生成交易计划（三种推演）

        Args:
            structure: 结构推理结果
            risk: 风控评估结果
            decision: 决策结果
            current_price: 当前价格

        Returns:
            TradingPlan: 交易计划
        """
        # 获取关键价位
        key_levels = structure.key_levels
        if key_levels:
            resistance_high = key_levels.resistance_zone.get("high", current_price * 1.05)
            resistance_low = key_levels.resistance_zone.get("low", current_price * 1.03)
            support_high = key_levels.support_zone.get("high", current_price * 0.97)
            support_low = key_levels.support_zone.get("low", current_price * 0.95)
        else:
            resistance_high = current_price * 1.05
            resistance_low = current_price * 1.03
            support_high = current_price * 0.97
            support_low = current_price * 0.95

        # 计算目标区间（价格的2-5%）
        long_target_high = resistance_high * 1.02
        long_target_low = resistance_high * 0.98
        short_target_high = support_low * 1.02
        short_target_low = support_low * 0.98

        # 做多推演
        long_scenario = {
            "trigger": f"跌破{support_low:.0f}后企稳，或突破{resistance_low:.0f}",
            "target_zone": {
                "high": round(long_target_high, 2),
                "low": round(long_target_low, 2)
            },
            "logic": self._get_long_logic(structure, decision),
            "reason": self._get_long_reason(structure)
        }

        # 做空推演
        short_scenario = {
            "trigger": f"反弹至{resistance_high:.0f}附近受阻，或跌破{support_high:.0f}",
            "target_zone": {
                "high": round(short_target_high, 2),
                "low": round(short_target_low, 2)
            },
            "logic": self._get_short_logic(structure, decision),
            "reason": self._get_short_reason(structure)
        }

        # 震荡推演
        sideways_scenario = {
            "range": {
                "high": round(resistance_low, 2),
                "low": round(support_high, 2)
            },
            "logic": "多空分歧，等待方向选择",
            "reason": self._get_sideways_reason(structure)
        }

        return TradingPlan(
            long_scenario=long_scenario,
            short_scenario=short_scenario,
            sideways_scenario=sideways_scenario
        )

    def _get_long_logic(self, structure: StructureState, decision: Decision) -> str:
        """获取做多思路"""
        if structure.trend == "bullish":
            return "趋势延续，跟随做多"
        elif structure.phase == "rebound":
            return "反弹延续，短线做多"
        else:
            return "突破确认后追多"

    def _get_long_reason(self, structure: StructureState) -> str:
        """获取做多理由"""
        parts = []
        if structure.evidence.get("bi"):
            parts.append(structure.evidence["bi"].split("，")[1] if "，" in structure.evidence["bi"] else "")
        if structure.evidence.get("macd"):
            parts.append(structure.evidence["macd"].split("，")[1] if "，" in structure.evidence["macd"] else "")
        return "，".join([p for p in parts if p]) or "结构支持做多"

    def _get_short_logic(self, structure: StructureState, decision: Decision) -> str:
        """获取做空思路"""
        if structure.trend == "bearish":
            return "趋势延续，跟随做空"
        elif structure.phase == "rebound":
            return "反弹衰竭，逢高做空"
        else:
            return "跌破确认后追空"

    def _get_short_reason(self, structure: StructureState) -> str:
        """获取做空理由"""
        parts = []
        if structure.evidence.get("bi"):
            parts.append(structure.evidence["bi"].split("，")[0] if "，" in structure.evidence["bi"] else "")
        if structure.evidence.get("macd"):
            parts.append(structure.evidence["macd"].split("，")[0] if "，" in structure.evidence["macd"] else "")
        return "，".join([p for p in parts if p]) or "结构支持做空"

    def _get_sideways_reason(self, structure: StructureState) -> str:
        """获取震荡理由"""
        if structure.phase == "exhaustion":
            return "末段动能减弱，等待方向选择"
        elif structure.phase == "range":
            return "多空平衡，震荡整理中"
        else:
            return "信号不明确，建议观望"

"""
解释引擎 (Explanation Engine)

职责：将分析结果转换为自然语言报告
⚠️ 这一层只负责"说人话"，不参与计算

输出格式：
- 交易决策
- 概率分析
- 主导周期分析
- 结构阶段
- 多周期方向评分
- 信号质量
- 关键价位
- 交易推演
"""

import logging
from typing import Dict, Any, List

from models.state_models import (
    StructureState,
    RiskProfile,
    Decision,
    TradingPlan,
    CycleScore,
    KeyLevels,
    SignalQuality
)

logger = logging.getLogger(__name__)


class ExplanationEngine:
    """
    解释引擎 - 将分析结果转换为自然语言

    输入: 前三层的结果
    输出: 自然语言报告
    """

    # 表情符号映射
    ACTION_EMOJI = {
        "BUY": "🟢 买入",
        "SELL": "🔴 卖出",
        "WAIT": "⚪️ 等待"
    }

    PHASE_EMOJI = {
        "起涨": "🌱",
        "延续": "📈",
        "加速": "🚀",
        "背离": "⚠️",
        "衰竭": "🔋",
        "转折预备": "🔄",
        "震荡整理": "➡️",
        "trend_start": "🌱",
        "trend_extend": "📈",
        "rebound": "↗️",
        "range": "➡️",
        "exhaustion": "🔋"
    }

    TREND_TYPE_EMOJI = {
        "主升": "🚀",
        "反弹": "↗️",
        "回调": "↘️",
        "下跌延续": "📉"
    }

    PROB_EMOJI = {
        "高": "🔥",
        "中": "➡️",
        "低": "⚠️"
    }

    RESONANCE_TYPE_EMOJI = {
        "强共振": "🔥",
        "趋势共振": "➡️",
        "无共振": "❌"
    }

    STRENGTH_EMOJI = {
        "强": "🔥",
        "中": "➡️",
        "弱": "⚠️",
        "失败": "❌"
    }

    def __init__(self):
        pass

    def generate(
        self,
        structure: StructureState,
        risk: RiskProfile,
        decision: Decision,
        trading_plan: TradingPlan
    ) -> str:
        """
        生成可读的分析报告

        Args:
            structure: 结构推理结果
            risk: 风控评估结果
            decision: 决策结果
            trading_plan: 交易计划

        Returns:
            str: 自然语言报告
        """
        logger.info("开始生成解释报告...")

        sections = []

        # 标题
        sections.append("📊 缠论结构推理报告")
        sections.append("=" * 60)

        # 1. 交易决策
        sections.append(self._format_decision(decision))

        # 2. 概率分析
        sections.append(self._format_probability(decision))

        # 3. 主导周期分析
        sections.append(self._format_dominant_cycle(structure))

        # 4. 结构阶段
        sections.append(self._format_phase(structure))

        # 5. 多周期方向评分
        sections.append(self._format_cycle_score(structure))

        # 6. 信号质量
        sections.append(self._format_signal_quality(structure, decision))

        # 7. 关键价位
        sections.append(self._format_key_levels(structure))

        # 8. 交易推演
        sections.append(self._format_trading_plan(trading_plan))

        # 结束线
        sections.append("=" * 60)

        return "\n\n".join(sections)

    def _format_decision(self, decision: Decision) -> str:
        """格式化交易决策"""
        action_emoji = self.ACTION_EMOJI.get(decision.action, f"❓ {decision.action}")
        prob_emoji = self.PROB_EMOJI.get(decision.probability_bias, "❓")

        # 共振显示
        if decision.resonance_strength > 0:
            strength_bar = "█" * int(decision.resonance_strength * 10)
            resonance_display = f"{strength_bar} {decision.resonance_strength*100:.0f}%"
            if decision.resonance_type:
                type_emoji = self.RESONANCE_TYPE_EMOJI.get(decision.resonance_type, "")
                resonance_display += f" ({type_emoji}{decision.resonance_type})"
        else:
            resonance_display = "❌ 无共振"

        # 系统评分
        score_display = f"{decision.system_score:.2f}/10"

        lines = [
            f"🎯 交易决策: {action_emoji}",
            f"   入场时机: {decision.entry_hint}",
            f"   概率偏向: {prob_emoji} {decision.probability_bias}",
            f"   多周期共振: {resonance_display}",
            f"   系统评分: {score_display}",
            f"   📌 结论: {decision.summary}"
        ]

        return "\n".join(lines)

    def _format_probability(self, decision: Decision) -> str:
        """格式化概率分析"""
        bullish = decision.bullish_prob
        bearish = decision.bearish_prob
        sideways = decision.sideways_prob

        # 概率柱状图
        bullish_bar = "█" * int(bullish * 10)
        bearish_bar = "█" * int(bearish * 10)
        sideways_bar = "█" * int(sideways * 10)

        conf_emoji = self.PROB_EMOJI.get(decision.confidence_level, "❓")

        lines = [
            "📈 概率分析:",
            f"   多头: {bullish_bar} {bullish*100:.0f}%",
            f"   空头: {bearish_bar} {bearish*100:.0f}%",
            f"   震荡: {sideways_bar} {sideways*100:.0f}%",
            f"   置信度: {conf_emoji} {decision.confidence_level}"
        ]

        return "\n".join(lines)

    def _format_dominant_cycle(self, structure: StructureState) -> str:
        """格式化主导周期分析"""
        lines = [
            "🔍 主导周期分析:",
            f"   📌 主导周期: {structure.dominant_cycle}",
            f"   理由: {structure.dominant_cycle_reason}"
        ]

        return "\n".join(lines)

    def _format_phase(self, structure: StructureState) -> str:
        """格式化结构阶段"""
        # 阶段显示
        phase_display = self._get_phase_display(structure.phase)
        phase_emoji = self.PHASE_EMOJI.get(structure.phase, "❓")

        # 趋势类型
        trend_type = structure.trend_type
        trend_emoji = self.TREND_TYPE_EMOJI.get(trend_type, "")

        evidence = structure.evidence

        lines = [
            f"📊 结构阶段: {phase_emoji} {phase_display}",
        ]

        # 显示趋势类型
        if trend_type:
            lines.append(f"   趋势性质: {trend_emoji} {trend_type}")

        # 显示证据
        lines.extend([
            f"   笔: {evidence.get('bi', 'N/A')}",
            f"   线段: {evidence.get('segment', 'N/A')}",
            f"   中枢: {evidence.get('zs', 'N/A')}",
            f"   MACD: {evidence.get('macd', 'N/A')}"
        ])

        # 阶段转换预警
        if structure.transition_warning:
            lines.append(f"   ⚠️ 预警: {structure.transition_warning}")

        return "\n".join(lines)

    def _get_phase_display(self, phase: str) -> str:
        """获取阶段显示文本"""
        phase_map = {
            "trend_start": "起涨（初段）",
            "trend_extend": "延续（中段）",
            "rebound": "反弹/回调",
            "range": "震荡整理",
            "exhaustion": "衰竭（末段）"
        }
        return phase_map.get(phase, phase)

    def _format_cycle_score(self, structure: StructureState) -> str:
        """格式化多周期方向评分"""
        cycle_score = structure.cycle_score
        if not cycle_score:
            return "📐 多周期方向评分: 无数据"

        dir_map = {1: "↑", -1: "↓", 0: "→"}

        daily_dir = dir_map.get(cycle_score.daily, "?")
        h4_dir = dir_map.get(cycle_score.h4, "?")
        h1_dir = dir_map.get(cycle_score.h1, "?")
        m15_dir = dir_map.get(cycle_score.m15, "?")

        # 判断偏向颜色
        bias = cycle_score.bias
        if bias == "偏多":
            bias_display = "🟢 偏多"
        elif bias == "偏空":
            bias_display = "🔴 偏空"
        else:
            bias_display = "⚪ 震荡"

        lines = [
            "📐 多周期方向评分:",
            f"   日线(×3): {daily_dir}  |  4H(×2): {h4_dir}  |  1H(×1.5): {h1_dir}  |  15M(×1): {m15_dir}",
            f"   加权分数: {cycle_score.weighted_score}  →  {bias_display}",
            f"   判断: {bias}"
        ]

        return "\n".join(lines)

    def _format_signal_quality(
        self,
        structure: StructureState,
        decision: Decision
    ) -> str:
        """格式化信号质量"""
        # 基于决策和结构判断信号质量
        if decision.action == "WAIT":
            signal_type = "无"
            signal_strength = "弱"
            has_edge = False
            reason = "信号不满足交易条件"
        else:
            signal_type = "买点" if decision.action == "BUY" else "卖点"
            signal_strength = "中" if decision.confidence >= 0.6 else "弱"
            has_edge = decision.resonance and decision.confidence >= 0.6
            reason = decision.reason

        strength_emoji = self.STRENGTH_EMOJI.get(signal_strength, "❓")
        edge_status = "✅ 有优势" if has_edge else "❌ 无优势"

        lines = [
            f"⚡ 信号质量: {signal_type}",
            f"   强度: {strength_emoji} {signal_strength}",
            f"   交易优势: {edge_status}",
            f"   理由: {reason}"
        ]

        return "\n".join(lines)

    def _format_key_levels(self, structure: StructureState) -> str:
        """格式化关键价位"""
        key_levels = structure.key_levels
        if not key_levels:
            return "📍 关键价位: 无数据"

        # 阻力区
        rz = key_levels.resistance_zone
        if rz and rz.get("high") and rz.get("low"):
            resistance_str = f"{rz.get('low')} - {rz.get('high')}"
            strength = rz.get("strength", "N/A")
            resistance_display = f"{resistance_str} (强度: {strength})"
        else:
            resistance_display = "N/A"

        # 支撑区
        sz = key_levels.support_zone
        if sz and sz.get("high") and sz.get("low"):
            support_str = f"{sz.get('low')} - {sz.get('high')}"
            strength = sz.get("strength", "N/A")
            support_display = f"{support_str} (强度: {strength})"
        else:
            support_display = "N/A"

        lines = [
            "📍 关键价位:",
            f"   上方阻力区: {resistance_display}",
            f"   下方支撑区: {support_display}",
            f"   突破确认: {key_levels.breakout_confirm or 'N/A'}",
            f"   跌破确认: {key_levels.breakdown_confirm or 'N/A'}"
        ]

        return "\n".join(lines)

    def _format_trading_plan(self, trading_plan: TradingPlan) -> str:
        """格式化交易推演"""
        lines = ["📋 交易推演:", ""]

        # 做多推演
        long_sc = trading_plan.long_scenario
        if long_sc:
            tz = long_sc.get("target_zone", {})
            target_str = f"{tz.get('low', 'N/A')} - {tz.get('high', 'N/A')}" if tz and tz.get("low") and tz.get("high") else "N/A"
            lines.extend([
                "🟢 做多推演:",
                f"   触发条件: {long_sc.get('trigger', 'N/A')}",
                f"   目标区间: {target_str}",
                f"   思路: {long_sc.get('logic', 'N/A')}",
                f"   理由: {long_sc.get('reason', 'N/A')}",
                ""
            ])

        # 做空推演
        short_sc = trading_plan.short_scenario
        if short_sc:
            tz = short_sc.get("target_zone", {})
            target_str = f"{tz.get('low', 'N/A')} - {tz.get('high', 'N/A')}" if tz and tz.get("low") and tz.get("high") else "N/A"
            lines.extend([
                "🔴 做空推演:",
                f"   触发条件: {short_sc.get('trigger', 'N/A')}",
                f"   目标区间: {target_str}",
                f"   思路: {short_sc.get('logic', 'N/A')}",
                f"   理由: {short_sc.get('reason', 'N/A')}",
                ""
            ])

        # 震荡推演
        side_sc = trading_plan.sideways_scenario
        if side_sc:
            rg = side_sc.get("range", {})
            range_str = f"{rg.get('low', 'N/A')} - {rg.get('high', 'N/A')}" if rg and rg.get("low") and rg.get("high") else "N/A"
            lines.extend([
                "🟡 震荡推演:",
                f"   区间范围: {range_str}",
                f"   思路: {side_sc.get('logic', 'N/A')}",
                f"   理由: {side_sc.get('reason', 'N/A')}"
            ])

        return "\n".join(lines)

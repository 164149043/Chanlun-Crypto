"""
风险叙事引擎 (Risk Narrative Engine)

职责：生成增强版风险提示，提供叙事风格的风险分析
⚠️ 只读输入，不修改决策

功能：
1. 资金管理心理提示
2. 假突破风险预警
3. 波动率压缩预警
4. 交易心理建议
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from models.state_models import (
    StructureState,
    RiskProfile,
    Decision
)

logger = logging.getLogger(__name__)


@dataclass
class RiskNarrative:
    """风险叙事结果"""
    # 资金管理提示
    money_management_tips: List[str] = field(default_factory=list)

    # 假突破风险
    fake_breakout_alerts: List[str] = field(default_factory=list)

    # 波动率预警
    volatility_alerts: List[str] = field(default_factory=list)

    # 交易心理建议
    psychological_advice: List[str] = field(default_factory=list)

    # 综合风险叙事
    narrative_summary: str = ""


class RiskNarrativeEngine:
    """
    风险叙事引擎 - 生成增强版风险提示

    输入：
    - StructureState: 结构状态
    - RiskProfile: 风控评估
    - Decision: 决策结果

    输出：
    - RiskNarrative: 风险叙事
    """

    # 风险等级阈值
    HIGH_RISK_THRESHOLD = 0.05  # ATR > 5% 为高风险
    LOW_VOLATILITY_THRESHOLD = 0.02  # ATR < 2% 为低波动

    def __init__(self):
        pass

    def analyze(
        self,
        structure: StructureState,
        risk: RiskProfile,
        decision: Decision
    ) -> RiskNarrative:
        """
        执行风险叙事分析

        Args:
            structure: 结构推理结果
            risk: 风控评估结果
            decision: 决策结果

        Returns:
            RiskNarrative: 风险叙事
        """
        logger.info("开始风险叙事分析...")

        narrative = RiskNarrative()

        # 1. 生成资金管理提示
        narrative.money_management_tips = self._generate_money_tips(risk, decision)

        # 2. 生成假突破风险预警
        narrative.fake_breakout_alerts = self._generate_fake_breakout_alerts(structure, decision)

        # 3. 生成波动率预警
        narrative.volatility_alerts = self._generate_volatility_alerts(risk, structure)

        # 4. 生成交易心理建议
        narrative.psychological_advice = self._generate_psychological_advice(structure, risk, decision)

        # 5. 生成综合叙事
        narrative.narrative_summary = self._generate_summary(narrative, structure, risk, decision)

        logger.info("风险叙事分析完成")
        return narrative

    def _generate_money_tips(self, risk: RiskProfile, decision: Decision) -> List[str]:
        """生成资金管理提示"""
        tips = []

        # 基于仓位建议
        if risk.position_size <= 0.15:
            tips.append("💡 当前建议极保守仓位，这是正确的风险管理方式")
            tips.append("💡 小仓位试探，确认方向后再加仓")
        elif risk.position_size <= 0.25:
            tips.append("💡 保守仓位适合当前市场环境，保持耐心")
        elif risk.position_size <= 0.35:
            tips.append("💡 标准仓位，注意设置止损保护本金")
        else:
            tips.append("⚠️ 仓位偏大，建议分批建仓降低风险")

        # 基于决策
        if decision.action == "WAIT":
            tips.append("💡 观望也是一种交易决策，保护本金是第一要务")

        # 基于盈亏比
        if risk.reward_ratio < 2.0:
            tips.append("⚠️ 当前盈亏比偏低，建议等待更好的入场点")
        elif risk.reward_ratio >= 3.0:
            tips.append("💡 盈亏比良好，适合执行交易计划")

        return tips

    def _generate_fake_breakout_alerts(
        self,
        structure: StructureState,
        decision: Decision
    ) -> List[str]:
        """生成假突破风险预警"""
        alerts = []

        # 基于结构阶段
        if structure.phase == "exhaustion":
            alerts.append("⚠️ 处于末段，突破信号可能为假突破")
            alerts.append("⚠️ 建议：等待突破后的回踩确认")

        if structure.phase == "range":
            alerts.append("⚠️ 震荡区间内，突破失败率较高")
            alerts.append("⚠️ 建议：在区间边界高抛低吸，而非追突破")

        # 基于周期冲突
        if structure.cycle_score:
            cs = structure.cycle_score
            if cs.daily * cs.h4 < 0:
                if cs.daily < 0 and cs.h4 > 0:
                    alerts.append("⚠️ 日线下跌中的4H反弹，突破可能是假突破")
                    alerts.append("⚠️ 建议：等待4H反弹失败信号再入场")
                elif cs.daily > 0 and cs.h4 < 0:
                    alerts.append("⚠️ 日线上涨中的4H回调，跌破可能是假跌破")
                    alerts.append("⚠️ 建议：等待4H回调企稳信号再入场")

        # 基于信号质量
        if decision.confidence < 0.6:
            alerts.append("⚠️ 信号置信度较低，突破可靠性存疑")

        if not alerts:
            alerts.append("✅ 当前无显著假突破风险")

        return alerts

    def _generate_volatility_alerts(
        self,
        risk: RiskProfile,
        structure: StructureState
    ) -> List[str]:
        """生成波动率预警"""
        alerts = []

        atr_percent = risk.atr_percent

        if atr_percent > self.HIGH_RISK_THRESHOLD:
            # 高波动
            alerts.append(f"🔴 高波动预警：ATR占比 {atr_percent*100:.1f}% > 5%")
            alerts.append("🔴 建议：")
            alerts.append("   - 扩大止损范围，避免被正常波动扫损")
            alerts.append("   - 减少仓位，降低单笔风险")
            alerts.append("   - 使用限价单而非市价单")

        elif atr_percent < self.LOW_VOLATILITY_THRESHOLD:
            # 低波动（波动率压缩）
            alerts.append(f"🟡 波动率压缩预警：ATR占比 {atr_percent*100:.1f}% < 2%")
            alerts.append("🟡 建议：")
            alerts.append("   - 可能即将出现大行情，提前做好准备")
            alerts.append("   - 关注突破方向，但不要提前押注")
            alerts.append("   - 设置突破预警，快速响应")

        else:
            # 正常波动
            alerts.append(f"🟢 波动率正常：ATR占比 {atr_percent*100:.1f}%")
            alerts.append("🟢 可以按正常策略执行")

        # 基于结构阶段补充
        if structure.phase == "exhaustion":
            alerts.append("⚠️ 末段通常伴随波动率收缩，注意突破方向")

        return alerts

    def _generate_psychological_advice(
        self,
        structure: StructureState,
        risk: RiskProfile,
        decision: Decision
    ) -> List[str]:
        """生成交易心理建议"""
        advice = []

        # 基于决策
        if decision.action == "WAIT":
            advice.append("🧘 耐心等待是交易的一部分")
            advice.append("🧘 市场永远在那里，不要急于入场")
            advice.append("🧘 宁可错过，不可做错")

        elif decision.action == "BUY":
            if structure.trend == "bearish":
                advice.append("🧘 逆势交易需要更强的心理承受力")
                advice.append("🧘 严格执行止损，不要抱有幻想")
            else:
                advice.append("🧘 顺势交易，保持冷静")
                advice.append("🧘 让利润奔跑，不要过早平仓")

        elif decision.action == "SELL":
            if structure.trend == "bullish":
                advice.append("🧘 逆势做空需要更强的心理承受力")
                advice.append("🧘 严格执行止损，不要抱有幻想")
            else:
                advice.append("🧘 顺势做空，保持冷静")
                advice.append("🧘 让利润奔跑，不要过早平仓")

        # 基于风险等级
        if risk.risk_level == "high":
            advice.append("🧘 高风险环境，保持警惕")
            advice.append("🧘 如果感到不安，可以降低仓位或观望")

        # 基于系统评分
        if decision.system_score < 6.0:
            advice.append("🧘 系统评分较低，信号不明确")
            advice.append("🧘 如果不确定，观望是最好的选择")

        return advice

    def _generate_summary(
        self,
        narrative: RiskNarrative,
        structure: StructureState,
        risk: RiskProfile,
        decision: Decision
    ) -> str:
        """生成综合风险叙事"""
        # 风险等级描述
        risk_desc = {
            "low": "低风险",
            "medium": "中等风险",
            "high": "高风险"
        }.get(risk.risk_level, "未知")

        # 决策描述
        action_desc = {
            "BUY": "做多",
            "SELL": "做空",
            "WAIT": "观望"
        }.get(decision.action, "未知")

        # 构建叙事
        summary = f"当前市场处于{structure.phase}阶段，"
        summary += f"建议{action_desc}，"
        summary += f"风险等级为{risk_desc}。"

        # 添加关键提示
        if structure.phase == "exhaustion":
            summary += "注意末段可能出现的假突破风险。"

        if risk.position_size <= 0.15:
            summary += "建议使用极保守仓位试探。"

        if decision.system_score < 6.0:
            summary += "系统评分较低，信号可靠性有限。"

        return summary

    def format_narrative(self, narrative: RiskNarrative) -> str:
        """
        格式化风险叙事

        Args:
            narrative: 风险叙事结果

        Returns:
            str: 格式化文本
        """
        lines = ["🛡 风险叙事增强:"]

        # 资金管理提示
        if narrative.money_management_tips:
            lines.append("")
            lines.append("   💰 资金管理:")
            for tip in narrative.money_management_tips:
                lines.append(f"      {tip}")

        # 假突破风险
        if narrative.fake_breakout_alerts:
            lines.append("")
            lines.append("   ⚠️ 假突破风险:")
            for alert in narrative.fake_breakout_alerts:
                lines.append(f"      {alert}")

        # 波动率预警
        if narrative.volatility_alerts:
            lines.append("")
            lines.append("   📊 波动率预警:")
            for alert in narrative.volatility_alerts:
                lines.append(f"      {alert}")

        # 交易心理建议
        if narrative.psychological_advice:
            lines.append("")
            lines.append("   🧘 交易心理:")
            for advice in narrative.psychological_advice:
                lines.append(f"      {advice}")

        # 综合叙事
        if narrative.narrative_summary:
            lines.append("")
            lines.append(f"   📝 总结: {narrative.narrative_summary}")

        return "\n".join(lines)
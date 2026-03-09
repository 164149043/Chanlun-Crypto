"""
冲突分析器 (Conflict Analyzer)

职责：分析多周期方向冲突，判断演化方向
⚠️ 只读输入，不修改决策

触发条件：
- abs(weighted_score) < 0.8 时触发
- 多周期方向不一致时触发

AI任务：
1. 解释多周期为何冲突
2. 判断冲突更可能向哪个方向演化
3. 识别"假突破风险"
"""

import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from models.state_models import (
    StructureState,
    CycleScore
)

logger = logging.getLogger(__name__)


@dataclass
class ConflictResult:
    """冲突分析结果"""
    # 是否存在冲突
    has_conflict: bool = False

    # 冲突类型
    conflict_type: str = ""  # "direction" | "strength" | "phase"

    # 冲突描述
    conflict_description: str = ""

    # 演化方向预测
    evolution_bias: str = ""  # "bullish" | "bearish" | "neutral"

    # 演化理由
    evolution_reason: str = ""

    # 假突破风险
    fake_breakout_risk: str = ""

    # 关键观察点
    key_watch_points: List[str] = field(default_factory=list)


class ConflictAnalyzer:
    """
    冲突分析器 - 分析多周期方向冲突

    触发条件：
    - abs(weighted_score) < 0.8
    - 多周期方向不一致

    输出：
    - 冲突描述
    - 演化方向预测
    - 假突破风险
    """

    # 冲突触发阈值
    CONFLICT_SCORE_THRESHOLD = 0.8  # 加权分数绝对值小于此值触发

    def __init__(self):
        pass

    def should_trigger(self, structure: StructureState) -> bool:
        """
        判断是否应该触发冲突分析

        Args:
            structure: 结构推理结果

        Returns:
            bool: 是否触发
        """
        if not structure.cycle_score:
            return False

        weighted_score = structure.cycle_score.weighted_score

        # 条件1：加权分数绝对值小于阈值
        if abs(weighted_score) < self.CONFLICT_SCORE_THRESHOLD:
            return True

        # 条件2：多周期方向不一致
        directions = [
            structure.cycle_score.daily,
            structure.cycle_score.h4,
            structure.cycle_score.h1,
            structure.cycle_score.m15
        ]

        positive_count = sum(1 for d in directions if d > 0)
        negative_count = sum(1 for d in directions if d < 0)

        # 如果有2个以上方向相同，但有2个以上方向相反，则存在冲突
        if positive_count >= 2 and negative_count >= 2:
            return True

        return False

    def analyze(self, structure: StructureState) -> ConflictResult:
        """
        执行冲突分析

        Args:
            structure: 结构推理结果

        Returns:
            ConflictResult: 冲突分析结果
        """
        logger.info("开始冲突分析...")

        result = ConflictResult()

        # 检查是否触发
        if not self.should_trigger(structure):
            result.has_conflict = False
            result.conflict_description = "多周期方向一致，无显著冲突"
            return result

        result.has_conflict = True

        # 分析冲突类型
        result.conflict_type = self._analyze_conflict_type(structure)

        # 生成冲突描述
        result.conflict_description = self._generate_conflict_description(structure)

        # 判断演化方向
        result.evolution_bias, result.evolution_reason = self._predict_evolution(structure)

        # 识别假突破风险
        result.fake_breakout_risk = self._identify_fake_breakout_risk(structure)

        # 生成关键观察点
        result.key_watch_points = self._generate_watch_points(structure)

        logger.info(f"冲突分析完成: {result.conflict_type}")
        return result

    def _analyze_conflict_type(self, structure: StructureState) -> str:
        """分析冲突类型"""
        cycle_score = structure.cycle_score
        if not cycle_score:
            return "unknown"

        # 方向冲突：大周期和小周期方向相反
        if cycle_score.daily * cycle_score.h4 < 0:
            return "direction"  # 方向冲突

        # 强度冲突：同方向但内部矛盾
        if cycle_score.daily * cycle_score.h1 < 0:
            return "strength"   # 强度冲突

        # 阶段冲突：趋势和阶段不匹配
        if structure.phase == "exhaustion" and abs(cycle_score.weighted_score) > 1:
            return "phase"      # 阶段冲突

        return "mixed"  # 混合冲突

    def _generate_conflict_description(self, structure: StructureState) -> str:
        """生成冲突描述"""
        cycle_score = structure.cycle_score
        if not cycle_score:
            return ""

        dir_map = {1: "上涨", -1: "下跌", 0: "震荡"}

        parts = [
            f"日线{dir_map.get(cycle_score.daily, '未知')}",
            f"4H{dir_map.get(cycle_score.h4, '未知')}",
            f"1H{dir_map.get(cycle_score.h1, '未知')}",
            f"15M{dir_map.get(cycle_score.m15, '未知')}"
        ]

        conflict_type = structure.phase

        description = f"多周期方向矛盾：{'，'.join(parts)}。"
        description += f"当前处于{conflict_type}阶段，方向选择不明确。"

        return description

    def _predict_evolution(self, structure: StructureState) -> tuple:
        """
        预测演化方向

        Returns:
            (evolution_bias, reason)
        """
        cycle_score = structure.cycle_score
        if not cycle_score:
            return "neutral", "数据不足"

        # 规则1：大级别优先
        if cycle_score.daily < 0:
            return "bearish", "日线趋势向下，小级别反弹可能衰竭"
        elif cycle_score.daily > 0:
            return "bullish", "日线趋势向上，小级别回调可能结束"

        # 规则2：看4H动能
        if cycle_score.h4 != 0:
            if cycle_score.h4 > 0:
                return "bullish", "4H动能向上，可能带动日线转折"
            else:
                return "bearish", "4H动能向下，可能带动日线转折"

        # 规则3：看阶段
        if structure.phase == "exhaustion":
            if structure.trend == "bearish":
                return "bearish", "末段衰竭，可能延续下跌"
            else:
                return "bullish", "末段衰竭，可能延续上涨"

        return "neutral", "多空力量均衡，等待方向选择"

    def _identify_fake_breakout_risk(self, structure: StructureState) -> str:
        """识别假突破风险"""
        risks = []

        cycle_score = structure.cycle_score
        if not cycle_score:
            return ""

        # 风险1：4H和1H方向相反
        if cycle_score.h4 * cycle_score.h1 < 0:
            if cycle_score.h4 > 0:
                risks.append("4H上涨但1H下跌，若1H继续走弱，4H反弹可能失败")
            else:
                risks.append("4H下跌但1H上涨，若1H动能不足，可能只是弱反弹")

        # 风险2：末段突破
        if structure.phase == "exhaustion":
            risks.append("处于末段，突破信号可能为假突破")

        # 风险3：量能不足（如果有证据）
        evidence = structure.evidence
        if evidence.get("macd") and "负" in evidence.get("macd", ""):
            if cycle_score.h4 > 0:
                risks.append("MACD负值区域，上涨动能可能不足")

        return "；".join(risks) if risks else "当前无显著假突破风险"

    def _generate_watch_points(self, structure: StructureState) -> List[str]:
        """生成关键观察点"""
        points = []

        # 观察点1：4H方向确认
        points.append("观察4H能否确认方向突破")

        # 观察点2：关键价位
        if structure.key_levels:
            if structure.key_levels.resistance_zone:
                high = structure.key_levels.resistance_zone.get("high", 0)
                if high > 0:
                    points.append(f"关注阻力位 {high:.0f} 附近反应")
            if structure.key_levels.support_zone:
                low = structure.key_levels.support_zone.get("low", 0)
                if low > 0:
                    points.append(f"关注支撑位 {low:.0f} 附近反应")

        # 观察点3：MACD变化
        points.append("观察MACD柱状图变化，判断动能转换")

        return points

    def format_result(self, result: ConflictResult) -> str:
        """
        格式化冲突分析结果

        Args:
            result: 冲突分析结果

        Returns:
            str: 格式化文本
        """
        if not result.has_conflict:
            return ""

        lines = [
            "⚡ 冲突分析:",
            f"   冲突类型: {result.conflict_type}",
            f"   冲突描述: {result.conflict_description}",
            "",
            f"   📊 演化方向: {result.evolution_bias}",
            f"   理由: {result.evolution_reason}",
            "",
            f"   ⚠️ 假突破风险: {result.fake_breakout_risk}",
            "",
            "   👀 关键观察点:"
        ]

        for point in result.key_watch_points:
            lines.append(f"      • {point}")

        return "\n".join(lines)
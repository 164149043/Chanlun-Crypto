"""
风控评估引擎 (Risk Engine)

职责：计算风险、止损、仓位
⚠️ 这一层只算风险，不管方向
⚠️ 纯数学计算，不使用AI

计算内容：
- ATR波动率
- 风险收益比
- 止损区间
- 建议仓位
"""

import logging
from typing import Dict, Any

from models.state_models import (
    StructureState,
    RiskProfile,
    Indicators
)

logger = logging.getLogger(__name__)


class RiskEngine:
    """
    风控评估引擎 - 评估风险和仓位

    输入:
      - structure: 结构推理结果
      - indicators: 技术指标（ATR、波动率、中枢距离）
    输出: RiskProfile
    """

    # 风控参数
    MAX_POSITION_SIZE = 0.5      # 最大仓位 50%
    MIN_POSITION_SIZE = 0.1      # 最小仓位 10%
    MIN_REWARD_RATIO = 2.0       # 最小盈亏比
    DEFAULT_REWARD_RATIO = 2.5   # 默认盈亏比

    # ATR倍数（用于止损）
    STOP_LOSS_ATR_MULTIPLIER = 1.5  # 止损距离 = 1.5 * ATR

    # 风险等级阈值
    ATR_LOW_THRESHOLD = 0.02     # ATR < 2% = 低风险
    ATR_HIGH_THRESHOLD = 0.05    # ATR > 5% = 高风险

    def __init__(self):
        pass

    def evaluate(self, structure: StructureState, indicators: Indicators) -> RiskProfile:
        """
        基于结构状态评估风险

        Args:
            structure: 结构推理结果
            indicators: 技术指标数据

        Returns:
            RiskProfile: 风控评估结果
        """
        logger.info("开始风控评估...")

        # 1. 计算ATR波动率
        atr = indicators.atr if indicators.atr > 0 else self._estimate_atr(indicators)
        atr_percent = indicators.atr_percent if indicators.atr_percent > 0 else self._calculate_atr_percent(atr, indicators.current_price)

        # 2. 评估风险等级
        risk_level = self._assess_risk_level(atr_percent, structure)

        # 3. 计算止损价位
        stop_loss_long, stop_loss_short = self._calculate_stop_loss(structure, indicators, atr)

        # 4. 计算止损区间
        stop_zone_long = self._calculate_stop_zone(stop_loss_long, indicators.current_price, "long")
        stop_zone_short = self._calculate_stop_zone(stop_loss_short, indicators.current_price, "short")

        # 5. 计算风险收益比
        reward_ratio = self._calculate_reward_ratio(structure, indicators)

        # 6. 计算建议仓位
        position_size = self._calculate_position_size(structure, risk_level, atr_percent)

        # 7. 生成仓位描述
        position_hint = self._get_position_hint(position_size)

        profile = RiskProfile(
            risk_level=risk_level,
            atr=atr,
            atr_percent=atr_percent,
            reward_ratio=reward_ratio,
            stop_loss_long=stop_loss_long,
            stop_loss_short=stop_loss_short,
            stop_zone_long=stop_zone_long,
            stop_zone_short=stop_zone_short,
            position_size=position_size,
            position_hint=position_hint
        )

        logger.info(f"风控评估完成: 风险等级={risk_level}, 仓位={position_hint}")
        return profile

    def _estimate_atr(self, indicators: Indicators) -> float:
        """
        估算ATR（如果没有提供）

        使用最高价和最低价的差来估算
        """
        if indicators.recent_high > 0 and indicators.recent_low > 0:
            # 使用最近高低点的20%作为ATR估算
            return (indicators.recent_high - indicators.recent_low) * 0.2
        elif indicators.current_price > 0:
            # 使用当前价格的3%作为默认ATR
            return indicators.current_price * 0.03
        else:
            return 0.0

    def _calculate_atr_percent(self, atr: float, current_price: float) -> float:
        """计算ATR占价格的百分比"""
        if current_price > 0 and atr > 0:
            return atr / current_price
        return 0.0

    def _assess_risk_level(self, atr_percent: float, structure: StructureState) -> str:
        """
        评估风险等级

        考虑因素：
        1. ATR波动率
        2. 结构强度
        3. 市场阶段
        """
        # 基于ATR的基础风险
        if atr_percent < self.ATR_LOW_THRESHOLD:
            base_risk = "low"
        elif atr_percent > self.ATR_HIGH_THRESHOLD:
            base_risk = "high"
        else:
            base_risk = "medium"

        # 根据结构阶段调整
        if structure.phase == "exhaustion":
            # 末段风险较高
            if base_risk == "low":
                return "medium"
            else:
                return "high"
        elif structure.phase == "range":
            # 震荡期风险中等
            return "medium"
        elif structure.phase == "trend_extend":
            # 趋势延续期风险较低
            return base_risk
        else:
            return base_risk

    def _calculate_stop_loss(
        self,
        structure: StructureState,
        indicators: Indicators,
        atr: float
    ) -> tuple:
        """
        计算止损价位

        做多止损 = 当前价格 - ATR * 倍数
        做空止损 = 当前价格 + ATR * 倍数

        Returns:
            (做多止损, 做空止损)
        """
        current_price = indicators.current_price

        if current_price <= 0:
            return 0.0, 0.0

        # 基于ATR的止损距离
        stop_distance = atr * self.STOP_LOSS_ATR_MULTIPLIER

        # 做多止损（在支撑区下方）
        stop_loss_long = current_price - stop_distance

        # 做空止损（在阻力区上方）
        stop_loss_short = current_price + stop_distance

        # 如果有支撑区信息，使用支撑区下沿
        if structure.key_levels and structure.key_levels.support_zone:
            support_low = structure.key_levels.support_zone.get("low", 0)
            if support_low > 0:
                stop_loss_long = min(stop_loss_long, support_low * 0.995)

        # 如果有阻力区信息，使用阻力区上沿
        if structure.key_levels and structure.key_levels.resistance_zone:
            resistance_high = structure.key_levels.resistance_zone.get("high", 0)
            if resistance_high > 0:
                stop_loss_short = max(stop_loss_short, resistance_high * 1.005)

        return round(stop_loss_long, 2), round(stop_loss_short, 2)

    def _calculate_stop_zone(
        self,
        stop_price: float,
        current_price: float,
        direction: str
    ) -> Dict[str, float]:
        """
        计算止损区间

        区间宽度 = 价格的 0.3-0.5%
        """
        if stop_price <= 0 or current_price <= 0:
            return {}

        # 区间宽度 = 当前价格的0.4%
        zone_width = current_price * 0.004

        if direction == "long":
            return {
                "high": round(stop_price + zone_width / 2, 2),
                "low": round(stop_price - zone_width / 2, 2)
            }
        else:
            return {
                "high": round(stop_price + zone_width / 2, 2),
                "low": round(stop_price - zone_width / 2, 2)
            }

    def _calculate_reward_ratio(
        self,
        structure: StructureState,
        indicators: Indicators
    ) -> float:
        """
        计算风险收益比

        基于结构强度和市场阶段
        """
        # 基础盈亏比
        base_ratio = self.DEFAULT_REWARD_RATIO

        # 根据结构强度调整
        if structure.strength >= 0.7:
            # 强结构，盈亏比高
            base_ratio = 3.0
        elif structure.strength >= 0.5:
            # 中等结构
            base_ratio = 2.5
        else:
            # 弱结构
            base_ratio = 2.0

        # 根据市场阶段调整
        if structure.phase == "trend_extend":
            # 趋势延续，盈亏比高
            base_ratio *= 1.2
        elif structure.phase == "exhaustion":
            # 末段，盈亏比低
            base_ratio *= 0.8

        return round(max(base_ratio, self.MIN_REWARD_RATIO), 1)

    def _calculate_position_size(
        self,
        structure: StructureState,
        risk_level: str,
        atr_percent: float
    ) -> float:
        """
        计算建议仓位

        考虑因素：
        1. 风险等级
        2. 结构强度
        3. ATR波动率
        """
        # 基于风险等级的基础仓位
        if risk_level == "low":
            base_size = 0.5   # 50%
        elif risk_level == "high":
            base_size = 0.15  # 15%
        else:
            base_size = 0.3   # 30%

        # 根据结构强度调整
        strength_factor = structure.strength  # 0.0 - 1.0

        # 根据ATR调整（高波动降低仓位）
        if atr_percent > 0.04:
            atr_factor = 0.7  # 高波动降低30%
        elif atr_percent > 0.03:
            atr_factor = 0.85
        else:
            atr_factor = 1.0

        # 计算最终仓位
        position_size = base_size * strength_factor * atr_factor

        # 限制范围
        position_size = max(self.MIN_POSITION_SIZE, min(position_size, self.MAX_POSITION_SIZE))

        return round(position_size, 2)

    def _get_position_hint(self, position_size: float) -> str:
        """生成仓位描述"""
        if position_size >= 0.4:
            return f"标准({int(position_size * 100)}%)"
        elif position_size >= 0.25:
            return f"保守({int(position_size * 100)}%)"
        else:
            return f"极保守({int(position_size * 100)}%)"

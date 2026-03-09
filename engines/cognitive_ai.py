"""
认知AI引擎 (Cognitive AI Engine)

职责：AI增强认知层，提供深度分析
⚠️ 这一层只做"认知增强"，不改决策

认知层组成：
- CognitiveAI: AI分析（情景推演、风险提醒）
- ConflictAnalyzer: 多周期冲突分析（条件触发）
- RiskNarrativeEngine: 风险叙事增强

核心原则：
- 决策由 DecisionEngine 做出，AI不改决策
- AI只提供认知增强，帮助理解市场
- AI失败不影响核心功能
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from models.state_models import (
    StructureState,
    RiskProfile,
    Decision,
    TradingPlan,
    CycleScore,
    KeyLevels
)

# 导入认知层子模块
from .conflict_analyzer import ConflictAnalyzer, ConflictResult
from .risk_narrative import RiskNarrativeEngine, RiskNarrative

logger = logging.getLogger(__name__)


# DeepSeek API 配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_MODEL = "deepseek-reasoner"
MAX_RETRIES = 3
RETRY_DELAY = 2


@dataclass
class StructureEvolutionPath:
    """结构演化路径"""
    scenario: str           # 场景名称
    trigger: str            # 触发条件
    probability: str        # 概率估计
    description: str        # 场景描述


@dataclass
class StructureEvolution:
    """结构演化分析"""
    current_state: str                              # 当前状态描述
    possible_paths: List[StructureEvolutionPath] = field(default_factory=list)


@dataclass
class ScenarioAnalysis:
    """情景分析"""
    best_case: str      # 最好情况
    base_case: str      # 基本情况
    worst_case: str     # 最差情况


@dataclass
class CognitiveInsight:
    """
    AI认知洞察结果

    AI只输出认知增强信息，不改决策
    """
    # 风险提醒列表
    risk_alerts: List[str] = field(default_factory=list)

    # 结构演化分析
    structure_evolution: Optional[StructureEvolution] = None

    # 情景分析
    scenario_analysis: Optional[ScenarioAnalysis] = None

    # 冲突分析（新增）
    conflict_result: Optional[ConflictResult] = None

    # 风险叙事（新增）
    risk_narrative: Optional[RiskNarrative] = None

    # 原始AI响应（用于调试）
    raw_response: str = ""

    # 是否成功
    success: bool = False

    # 错误信息
    error: str = ""


class CognitiveAI:
    """
    认知AI引擎 - AI增强认知层

    输入: 引擎输出（结构化数据）
    输出: CognitiveInsight（认知增强信息）

    ⚠️ AI不改决策，只提供认知增强
    """

    def __init__(self, api_key: str = None, model: str = DEFAULT_MODEL):
        """
        初始化认知AI引擎

        Args:
            api_key: DeepSeek API密钥
            model: 模型名称
        """
        self.api_key = api_key
        self.model = model

    def analyze(
        self,
        structure: StructureState,
        risk: RiskProfile,
        decision: Decision,
        trading_plan: TradingPlan,
        current_price: float = 0,
        symbol: str = ""
    ) -> CognitiveInsight:
        """
        执行AI认知分析

        Args:
            structure: 结构推理结果
            risk: 风控评估结果
            decision: 决策结果
            trading_plan: 交易计划
            current_price: 当前价格
            symbol: 交易对

        Returns:
            CognitiveInsight: AI认知洞察
        """
        logger.info("开始认知层分析...")

        insight = CognitiveInsight()

        # 1. 冲突分析（条件触发）
        conflict_analyzer = ConflictAnalyzer()
        if conflict_analyzer.should_trigger(structure):
            logger.info("触发冲突分析...")
            insight.conflict_result = conflict_analyzer.analyze(structure)

        # 2. 风险叙事增强
        risk_narrative_engine = RiskNarrativeEngine()
        insight.risk_narrative = risk_narrative_engine.analyze(structure, risk, decision)

        # 3. AI深度分析（可选，需要API密钥）
        if self.api_key:
            logger.info("执行AI深度分析...")

            # 构建AI输入
            ai_input = self._build_ai_input(
                structure, risk, decision, trading_plan, current_price, symbol
            )

            # 构建AI提示词
            prompt = self._build_prompt(ai_input)

            # 调用AI API
            response_text = self._call_api(prompt)

            if response_text:
                # 解析AI响应
                insight = self._parse_response(response_text, insight)
                insight.raw_response = response_text
            else:
                insight.error = "AI API调用失败"
        else:
            logger.info("未配置API密钥，跳过AI深度分析")
            # 即使没有AI，认知层仍然提供价值
            insight.success = True
            insight.error = "仅使用规则引擎（未配置AI）"

        # 标记成功
        if insight.conflict_result or insight.risk_narrative or insight.structure_evolution:
            insight.success = True

        logger.info(f"认知层分析完成: 冲突={insight.conflict_result is not None}, 叙事={insight.risk_narrative is not None}")
        return insight

    def _build_ai_input(
        self,
        structure: StructureState,
        risk: RiskProfile,
        decision: Decision,
        trading_plan: TradingPlan,
        current_price: float,
        symbol: str
    ) -> Dict[str, Any]:
        """
        构建AI输入数据

        ⚠️ 只传递必要信息，AI不改决策
        """
        # 构建结构数据
        structure_data = {
            "dominant_cycle": structure.dominant_cycle,
            "trend": structure.trend,
            "trend_type": structure.trend_type,
            "phase": structure.phase,
            "position": structure.position,
            "strength": structure.strength
        }

        # 构建周期评分
        cycle_score_data = None
        if structure.cycle_score:
            cycle_score_data = {
                "daily": structure.cycle_score.daily,
                "h4": structure.cycle_score.h4,
                "h1": structure.cycle_score.h1,
                "m15": structure.cycle_score.m15,
                "weighted_score": structure.cycle_score.weighted_score,
                "bias": structure.cycle_score.bias
            }

        # 构建概率数据
        probability_data = {
            "bull_prob": decision.bullish_prob,
            "bear_prob": decision.bearish_prob,
            "range_prob": decision.sideways_prob
        }

        # 构建关键价位
        key_levels_data = None
        if structure.key_levels:
            key_levels_data = {
                "resistance": [
                    structure.key_levels.resistance_zone.get("low", 0),
                    structure.key_levels.resistance_zone.get("high", 0)
                ],
                "support": [
                    structure.key_levels.support_zone.get("low", 0),
                    structure.key_levels.support_zone.get("high", 0)
                ]
            }

        # 构建风险数据
        risk_data = {
            "risk_level": risk.risk_level,
            "reward_ratio": risk.reward_ratio,
            "position_size": risk.position_size
        }

        # 构建决策数据
        decision_data = {
            "action": decision.action,
            "confidence": decision.confidence,
            "system_score": decision.system_score
        }

        return {
            "symbol": symbol,
            "current_price": current_price,
            "structure": structure_data,
            "cycle_score": cycle_score_data,
            "probability": probability_data,
            "key_levels": key_levels_data,
            "risk": risk_data,
            "decision": decision_data
        }

    def _build_prompt(self, ai_input: Dict[str, Any]) -> str:
        """
        构建AI提示词

        ⚠️ 强调AI只做认知增强，不改决策
        """
        input_json = json.dumps(ai_input, ensure_ascii=False, indent=2)

        prompt = f"""
你是一名专业的市场结构分析师，负责提供**认知增强分析**。

【重要原则】
⚠️ 你**不负责做交易决策**，决策已由系统引擎完成。
⚠️ 你的任务是帮助用户**理解市场结构**和**潜在风险**。

【输入数据】
```json
{input_json}
```

【任务】
基于上述数据，提供以下认知增强分析：

1. **风险提醒** (risk_alerts)
   - 列出3-5条当前市场的主要风险点
   - 关注：结构矛盾、动能衰竭、关键价位、波动风险
   - 每条以⚠️开头，简洁明了

2. **结构演化路径** (structure_evolution)
   - 描述当前市场状态
   - 列出2-3种可能的演化路径：
     - scenario: 场景名称（如"继续下跌"、"震荡整理"、"反转上涨"）
     - trigger: 触发该场景的价格条件
     - probability: 概率估计（如"40%"）
     - description: 简要描述

3. **情景分析** (scenario_analysis)
   - best_case: 最好情况（价格目标、结构变化）
   - base_case: 基本情况（最可能发生的情况）
   - worst_case: 最差情况（风险下限）

【输出格式】
严格按照以下JSON格式输出，不要输出其他内容：

```json
{{
  "risk_alerts": [
    "⚠️ 风险提醒1",
    "⚠️ 风险提醒2",
    "⚠️ 风险提醒3"
  ],
  "structure_evolution": {{
    "current_state": "当前市场状态描述",
    "possible_paths": [
      {{
        "scenario": "场景名称",
        "trigger": "触发条件",
        "probability": "概率",
        "description": "场景描述"
      }}
    ]
  }},
  "scenario_analysis": {{
    "best_case": "最好情况描述",
    "base_case": "基本情况描述",
    "worst_case": "最差情况描述"
  }}
}}
```

【注意事项】
- 只输出JSON，不要输出其他文字
- 风险提醒要具体，基于数据中的结构信息
- 演化路径要合理，概率之和应接近100%
- 情景分析要客观，不偏向多空任何一方
"""
        return prompt

    def _call_api(self, prompt: str) -> Optional[str]:
        """
        调用DeepSeek API

        Args:
            prompt: 提示词

        Returns:
            API响应文本，失败返回None
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # 降低随机性
            "max_tokens": 2000
        }

        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"API 调用尝试 {attempt + 1}/{MAX_RETRIES}")
                response = requests.post(
                    DEEPSEEK_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=120
                )
                response.raise_for_status()

                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                if content:
                    logger.info(f"API 响应长度: {len(content)} 字符")
                    return content

            except requests.exceptions.Timeout:
                logger.warning(f"请求超时，尝试 {attempt + 1}/{MAX_RETRIES}")
                if attempt < MAX_RETRIES - 1:
                    import time
                    time.sleep(RETRY_DELAY * (attempt + 1))

            except requests.exceptions.RequestException as e:
                logger.error(f"API 请求失败: {e}")
                if attempt < MAX_RETRIES - 1:
                    import time
                    time.sleep(RETRY_DELAY * (attempt + 1))

        return None

    def _parse_response(self, response_text: str, insight: CognitiveInsight = None) -> CognitiveInsight:
        """
        解析AI响应

        Args:
            response_text: AI响应文本
            insight: 现有的洞察对象（可选）

        Returns:
            CognitiveInsight: 解析后的认知洞察
        """
        if insight is None:
            insight = CognitiveInsight(raw_response=response_text)
        else:
            insight.raw_response = response_text

        try:
            # 尝试提取JSON
            json_text = self._extract_json(response_text)
            if not json_text:
                insight.error = "无法从响应中提取JSON"
                return insight

            data = json.loads(json_text)

            # 解析风险提醒
            risk_alerts = data.get("risk_alerts", [])
            if isinstance(risk_alerts, list):
                insight.risk_alerts = [str(r) for r in risk_alerts]

            # 解析结构演化
            evolution_data = data.get("structure_evolution", {})
            if evolution_data:
                paths = []
                for path_data in evolution_data.get("possible_paths", []):
                    paths.append(StructureEvolutionPath(
                        scenario=path_data.get("scenario", ""),
                        trigger=path_data.get("trigger", ""),
                        probability=path_data.get("probability", ""),
                        description=path_data.get("description", "")
                    ))
                insight.structure_evolution = StructureEvolution(
                    current_state=evolution_data.get("current_state", ""),
                    possible_paths=paths
                )

            # 解析情景分析
            scenario_data = data.get("scenario_analysis", {})
            if scenario_data:
                insight.scenario_analysis = ScenarioAnalysis(
                    best_case=scenario_data.get("best_case", ""),
                    base_case=scenario_data.get("base_case", ""),
                    worst_case=scenario_data.get("worst_case", "")
                )

            insight.success = True

        except json.JSONDecodeError as e:
            insight.error = f"JSON解析失败: {e}"
        except Exception as e:
            insight.error = f"解析错误: {e}"

        return insight

    def _extract_json(self, text: str) -> Optional[str]:
        """
        从文本中提取JSON

        Args:
            text: 可能包含JSON的文本

        Returns:
            JSON字符串，失败返回None
        """
        # 尝试直接解析
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            pass

        # 尝试提取代码块中的JSON
        import re
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, text)
        for match in matches:
            try:
                json.loads(match)
                return match
            except json.JSONDecodeError:
                continue

        # 尝试提取花括号内容
        brace_pattern = r'\{[\s\S]*\}'
        match = re.search(brace_pattern, text)
        if match:
            try:
                json.loads(match.group())
                return match.group()
            except json.JSONDecodeError:
                pass

        return None

    def format_insight(self, insight: CognitiveInsight) -> str:
        """
        格式化认知洞察为可读文本

        Args:
            insight: 认知洞察

        Returns:
            格式化后的文本
        """
        if not insight.success:
            return f"⚠️ AI认知分析失败: {insight.error}"

        lines = []
        lines.append("🧠 AI认知分析")
        lines.append("=" * 60)

        # 风险提醒
        if insight.risk_alerts:
            lines.append("\n⚠️ 风险提醒:")
            for alert in insight.risk_alerts:
                lines.append(f"   {alert}")

        # 结构演化
        if insight.structure_evolution:
            lines.append("\n📊 结构演化:")
            lines.append(f"   当前状态: {insight.structure_evolution.current_state}")
            lines.append("   可能路径:")
            for path in insight.structure_evolution.possible_paths:
                lines.append(f"     • {path.scenario}: {path.trigger} → {path.probability}")
                lines.append(f"       {path.description}")

        # 情景分析
        if insight.scenario_analysis:
            lines.append("\n🎯 情景分析:")
            lines.append(f"   🟢 最好: {insight.scenario_analysis.best_case}")
            lines.append(f"   ⚪ 基准: {insight.scenario_analysis.base_case}")
            lines.append(f"   🔴 最差: {insight.scenario_analysis.worst_case}")

        # 冲突分析（新增）
        if insight.conflict_result and insight.conflict_result.has_conflict:
            conflict_analyzer = ConflictAnalyzer()
            lines.append("\n" + conflict_analyzer.format_result(insight.conflict_result))

        # 风险叙事（新增）
        if insight.risk_narrative:
            risk_engine = RiskNarrativeEngine()
            lines.append("\n" + risk_engine.format_narrative(insight.risk_narrative))

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)

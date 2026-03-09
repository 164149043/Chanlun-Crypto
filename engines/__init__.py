"""
引擎模块 - 4层引擎架构 + 认知层

🧠 StructureEngine - 结构推理引擎（理解市场发生了什么）
🛡 RiskEngine - 风控评估引擎（评估风险，纯数学计算）
⚖ DecisionEngine - 决策融合引擎（综合结构和风控做决策）
🗣 ExplanationEngine - 解释引擎（自然语言输出）

🔮 认知层（CognitiveLayer）：
   - CognitiveAI - 认知AI引擎（AI增强认知，不改决策）
   - ConflictAnalyzer - 冲突分析器（多周期冲突解析）
   - RiskNarrativeEngine - 风险叙事引擎（增强版风险提示）
"""

from .structure_engine import StructureEngine
from .risk_engine import RiskEngine
from .decision_engine import DecisionEngine
from .explanation_engine import ExplanationEngine
from .cognitive_ai import CognitiveAI, CognitiveInsight
from .conflict_analyzer import ConflictAnalyzer, ConflictResult
from .risk_narrative import RiskNarrativeEngine, RiskNarrative

__all__ = [
    # 核心引擎
    "StructureEngine",
    "RiskEngine",
    "DecisionEngine",
    "ExplanationEngine",
    # 认知层
    "CognitiveAI",
    "CognitiveInsight",
    "ConflictAnalyzer",
    "ConflictResult",
    "RiskNarrativeEngine",
    "RiskNarrative",
]

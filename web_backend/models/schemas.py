"""
Pydantic 数据模型 - API 请求和响应模型
"""

from typing import List, Literal, Optional
from pydantic import BaseModel


# ============================================
# 类型别名
# ============================================

# 交易对类型
Symbol = Literal["BTCUSDT", "ETHUSDT"]

# 持仓类型
PositionType = Literal["LONG", "SHORT", "NONE"]


# ============================================
# 持仓信息模型
# ============================================

class PositionInfo(BaseModel):
    """持仓信息"""
    position_type: PositionType = "NONE"  # LONG/SHORT/NONE
    entry_price: Optional[float] = None   # 开仓均价（NONE时不需要）


# ============================================
# K 线数据模型
# ============================================

class KlineData(BaseModel):
    """K 线数据"""
    time: int       # 时间戳
    open: float     # 开盘价
    high: float     # 最高价
    low: float      # 最低价
    close: float    # 收盘价
    volume: float   # 成交量


# ============================================
# 分析请求模型
# ============================================

class AnalysisRequest(BaseModel):
    """分析请求"""
    symbol: str  # "BTCUSDT" | "ETHUSDT"
    position: Optional[PositionInfo] = None  # 持仓信息（可选）


# ============================================
# SSE 事件模型
# ============================================

class SSEEvent(BaseModel):
    """SSE 事件数据"""
    stage: str      # fetching | committee_a | committee_b | committee_c | judge | complete | error
    message: str    # 状态消息
    content: str = ""  # 当前输出内容
    progress: float = 0.0  # 进度 0.0 - 1.0


# ============================================
# 委员输出模型
# ============================================

class CommitteeOutput(BaseModel):
    """委员输出"""
    id: str                 # committee_a | committee_b | committee_c
    name: str               # 委员A | 委员B | 委员C
    role: str               # 保守派 | 中立派 | 激进派
    temperature: float      # 温度参数
    content: str = ""       # 输出内容
    is_streaming: bool = False  # 是否正在流式输出


class JudgeOutput(BaseModel):
    """裁决官输出"""
    content: str = ""
    is_streaming: bool = False


# ============================================
# 分析状态模型
# ============================================

class AnalysisState(BaseModel):
    """分析状态"""
    symbol: Optional[str] = None
    is_analyzing: bool = False
    progress: float = 0.0
    stage: str = "idle"  # idle | fetching | committee_a | committee_b | committee_c | judge | complete | error
    committees: List[CommitteeOutput] = []
    judge: Optional[JudgeOutput] = None
    error: Optional[str] = None

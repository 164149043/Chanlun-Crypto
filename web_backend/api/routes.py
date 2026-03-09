"""
API 路由 - REST API 和 SSE 端点
"""

import logging
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from web_backend.models.schemas import KlineData, AnalysisRequest
from web_backend.models.schemas import Symbol
from web_backend.api.sse import stream_analyze_symbol

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# 常量配置
# ============================================

SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT"]


# ============================================
# API 端点
# ============================================

@router.get("/symbols")
async def get_symbols() -> List[str]:
    """
    获取支持的交易对列表
    """
    return SUPPORTED_SYMBOLS


@router.get("/kline/{symbol}")
async def get_kline(
    symbol: str,
    interval: str = "1d",
    limit: int = 200,
) -> List[KlineData]:
    """
    获取 K 线数据

    Args:
        symbol: 交易对 (BTCUSDT / ETHUSDT)
        interval: 周期 (1m, 5m, 15m, 1h, 4h, 1d)
        limit: 数量限制
    """
    if symbol not in SUPPORTED_SYMBOLS:
        raise HTTPException(status_code=400, detail=f"不支持的交易对: {symbol}")

    try:
        # 导入缠论相关模块
        from api.sse import stream_analyze_symbol

        from Chan import CChan
        from ChanConfig import CChanConfig
        from Common.CEnum import KL_TYPE
        from datetime import datetime, timedelta

        # 周期映射
        kl_type_map = {
            "1m": KL_TYPE.K_1M,
            "5m": KL_TYPE.K_5M,
            "15m": KL_TYPE.K_15M,
            "1h": KL_TYPE.K_60M,
            "4h": KL_TYPE.K_4H,
            "1d": KL_TYPE.K_DAY,
        }

        kl_type = kl_type_map.get(interval, KL_TYPE.K_DAY)

        # 计算开始时间
        days = 120 if kl_type == KL_TYPE.K_DAY else 60
        begin_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # 获取数据
        chan = CChan(
            code=symbol,
            data_src="custom:binanceAPI.BinanceAPI",
            begin_time=begin_date,
            lv_list=[kl_type],
            config=CChanConfig(),
        )

        klines = []
        kl_datas = chan.kl_datas
        kl = kl_datas.get(kl_type) if isinstance(kl_datas, dict) else None

        if kl and getattr(kl, "lst", None):
            for merged in kl.lst:
                if not getattr(merged, "lst", None):
                    continue
                for unit in merged.lst:
                    try:
                        klines.append(KlineData(
                            time=int(unit.time.timestamp()),
                            open=float(unit.open),
                            high=float(unit.high),
                            low=float(unit.low),
                            close=float(unit.close),
                            volume=float(unit.trade_info.metric.get("volume", 0)) if unit.trade_info else 0,
                        ))
                    except Exception as e:
                        logger.warning(f"解析 K 线数据失败: {e}")
                        continue

        return klines[-limit:] if len(klines) > limit else klines

    except Exception as e:
        logger.error(f"获取 K 线数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取 K 线数据失败: {str(e)}")


@router.post("/analyze/stream")
async def analyze_stream(request: AnalysisRequest):
    """
    SSE 流式分析接口

    返回 Server-Sent Events 流，每个事件包含分析进度和内容

    Args:
        request: 分析请求，包含 symbol 和可选的 position 信息
    """

    if request.symbol not in SUPPORTED_SYMBOLS:
        raise HTTPException(status_code=400, detail=f"不支持的交易对: {request.symbol}")

    return StreamingResponse(
        stream_analyze_symbol(request.symbol, position=request.position),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

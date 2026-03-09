"""
FastAPI 后端入口 - Bento Grid Web 应用后端

运行方式 (从项目根目录 chan.py 运行):
    cd chan.py
    python -m uvicorn web_backend.main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
import sys
import os

# 添加项目根目录到 Python 路径，以便导入 ai_strategy_engine 等模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web_backend.api.routes import router as api_router

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="Chan.py Analysis API",
    description="缠论分析 API - 三委员 + 裁决官机制",
    version="1.0.0",
)

# CORS 配置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """根路径 - API 信息"""
    return {
        "name": "Chan.py Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "symbols": "/api/symbols",
            "kline": "/api/kline/{symbol}",
            "analyze_stream": "/api/analyze/stream",
        },
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_backend.main:app", host="0.0.0.0", port=8000, reload=True)

"""
Vercel FastAPI 入口点

Vercel 原生支持 FastAPI，无需 Mangum 适配器。
直接导出 FastAPI app 对象即可。
"""

import sys
import os

# 获取项目根目录（api目录的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加项目根目录到 Python 路径（确保在列表开头）
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 直接导出 FastAPI 应用
from web_backend.main import app

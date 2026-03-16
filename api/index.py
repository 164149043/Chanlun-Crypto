"""
Vercel FastAPI 入口点

Vercel 会自动识别 api/ 目录下的 Python 文件作为 Serverless Functions。
此文件作为 FastAPI 应用的入口点。
"""

import sys
import os

# 获取项目根目录（api目录的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加项目根目录到 Python 路径（确保在列表开头）
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 导入 FastAPI 应用
from web_backend.main import app

# 使用 Mangum 包装 FastAPI 应用为 Vercel 兼容的 ASGI 应用
from mangum import Mangum
handler = Mangum(app)

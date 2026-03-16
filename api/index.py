"""
Vercel FastAPI 入口点

Vercel 会自动识别 api/ 目录下的 Python 文件作为 Serverless Functions。
此文件作为 FastAPI 应用的入口点。
"""

import sys
import os

# 添加项目根目录到 Python 路径
# Vercel 运行时，当前目录是项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入并导出 FastAPI 应用
from web_backend.main import app

# Vercel 要求的入口点
handler = app

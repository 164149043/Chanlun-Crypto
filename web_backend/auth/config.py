"""认证配置 - 从环境变量读取账号密码"""

import os

# 账号配置（通过环境变量设置）
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin@123.com")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "chanlun2026")

# JWT 配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "chanlun-crypto-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

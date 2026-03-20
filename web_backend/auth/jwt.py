"""JWT 工具函数"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from .config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_HOURS


def create_token(username: str) -> str:
    """创建 JWT Token"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> str | None:
    """验证 JWT Token，返回用户名或 None"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

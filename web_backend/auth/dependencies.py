"""认证依赖 - 用于保护其他路由"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt import verify_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """获取当前认证用户，用于路由保护"""
    user = verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="未授权访问")
    return user

"""认证路由"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .config import AUTH_USERNAME, AUTH_PASSWORD
from .jwt import create_token, verify_token


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


class VerifyResponse(BaseModel):
    valid: bool
    user: str | None = None


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录"""
    if request.username != AUTH_USERNAME or request.password != AUTH_PASSWORD:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_token(request.username)
    return LoginResponse(token=token)


@router.get("/verify", response_model=VerifyResponse)
async def verify(token: str):
    """验证 Token 有效性"""
    user = verify_token(token)
    if user:
        return VerifyResponse(valid=True, user=user)
    return VerifyResponse(valid=False)

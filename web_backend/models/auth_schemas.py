"""认证相关的 Pydantic 模型"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


class VerifyResponse(BaseModel):
    valid: bool
    user: str | None = None

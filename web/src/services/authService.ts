/**
 * 认证 API 服务
 */

import type { LoginRequest, LoginResponse, VerifyResponse } from '../types/auth';

// 生产环境(Vercel): VITE_API_BASE 为空字符串，使用相对路径
// 开发环境: VITE_API_BASE 为 http://localhost:8000
const API_BASE = import.meta.env.VITE_API_BASE ?? '';

/**
 * 用户登录
 */
export async function loginApi(request: LoginRequest): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '登录失败' }));
    throw new Error(error.detail || '登录失败');
  }

  return response.json();
}

/**
 * 验证 Token 有效性
 */
export async function verifyTokenApi(token: string): Promise<VerifyResponse> {
  const response = await fetch(`${API_BASE}/api/auth/verify?token=${token}`);

  if (!response.ok) {
    return { valid: false };
  }

  return response.json();
}

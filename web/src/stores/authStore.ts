/**
 * 认证状态管理 - Zustand + persist
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthState } from '../types/auth';
import { loginApi, verifyTokenApi } from '../services/authService';

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      token: null,

      login: async (username: string, password: string) => {
        try {
          const response = await loginApi({ username, password });
          set({ isAuthenticated: true, token: response.token });
          return true;
        } catch {
          return false;
        }
      },

      logout: () => {
        set({ isAuthenticated: false, token: null });
      },

      checkAuth: async () => {
        const { token } = get();
        if (!token) {
          set({ isAuthenticated: false });
          return false;
        }

        try {
          const result = await verifyTokenApi(token);
          if (result.valid) {
            set({ isAuthenticated: true });
            return true;
          } else {
            set({ isAuthenticated: false, token: null });
            return false;
          }
        } catch {
          set({ isAuthenticated: false, token: null });
          return false;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);

/**
 * 路由保护组件
 */

import { useEffect, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { AnimatedLoginPage } from './AnimatedLoginPage';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, token, checkAuth } = useAuthStore();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const verify = async () => {
      if (token) {
        await checkAuth();
      }
      setChecking(false);
    };
    verify();
  }, [token, checkAuth]);

  if (checking) {
    return (
      <div className="min-h-screen bg-bento-bg flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AnimatedLoginPage />;
  }

  return <>{children}</>;
}

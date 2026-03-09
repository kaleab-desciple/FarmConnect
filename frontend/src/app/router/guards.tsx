import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { UserRole } from '../config/roles';

interface AuthGuardProps {
  children: ReactNode;
  requireAuth?: boolean;
  allowedRoles?: UserRole[];
  fallbackPath?: string;
}

export function AuthGuard({
  children,
  requireAuth = false,
  allowedRoles,
  fallbackPath = '/login',
}: AuthGuardProps) {
  const location = useLocation();
  const { isAuthenticated, user } = useAuthStore();
  
  // Not authenticated but auth is required
  if (requireAuth && !isAuthenticated) {
    return (
      <Navigate
        to={fallbackPath}
        state={{ from: location }}
        replace
      />
    );
  }
  
  // Authenticated but role not allowed
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return (
      <Navigate
        to="/unauthorized"
        replace
      />
    );
  }
  
  // Authenticated user trying to access login page
  if (!requireAuth && isAuthenticated && location.pathname === '/login') {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }
  
  return <>{children}</>;
}

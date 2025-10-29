/**
 * Auth Guard Component
 * Higher-order component for protecting components
 */

import { useAuth } from '@clerk/clerk-react';
import { CLERK_ROUTES } from '@/shared/config/clerk';
import { Navigate } from 'react-router-dom';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requireGuest?: boolean;
  fallback?: React.ReactNode;
}

export const AuthGuard = ({ 
  children, 
  requireAuth = false, 
  requireGuest = false,
  fallback 
}: AuthGuardProps) => {
  const { isSignedIn, isLoaded } = useAuth();

  if (!isLoaded) {
    return fallback || (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (requireAuth && !isSignedIn) {
    return <Navigate to={CLERK_ROUTES.SIGN_IN} replace />;
  }

  if (requireGuest && isSignedIn) {
    return <Navigate to={CLERK_ROUTES.DASHBOARD} replace />;
  }

  return <>{children}</>;
};

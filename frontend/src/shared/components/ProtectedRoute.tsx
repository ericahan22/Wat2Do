// src/components/ProtectedRoute.jsx
import { useAuth } from '@clerk/clerk-react';
import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

function ProtectedRoute({ children, redirectTo = '/auth/sign-in' }: ProtectedRouteProps) {
  const { isLoaded, isSignedIn } = useAuth();

  // Wait until Clerk has loaded its state
  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  // If the user is signed in, render the children
  if (isSignedIn) {
    return <>{children}</>;
  }

  // If the user is not signed in, redirect to sign in
  return <Navigate to={redirectTo} replace />;
}

export default ProtectedRoute;
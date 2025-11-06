// src/components/ProtectedRoute.jsx
import { useAuth, useUser } from '@clerk/clerk-react';
import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
  allowAdmins?: boolean;
}

function ProtectedRoute({ children, redirectTo = '/auth/sign-in', allowAdmins = false }: ProtectedRouteProps) {
  const { isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();

  // Wait until Clerk has loaded its state
  if (!isLoaded) {
    return <div>Loading...</div>;
  }

  // If the user is signed in and is an admin, redirect to /admin (unless allowAdmins is true)
  if (isSignedIn) {
    const isAdmin = user?.publicMetadata?.role === 'admin';
    if (isAdmin && !allowAdmins) {
      return <Navigate to="/admin" replace />;
    }
    // Otherwise render the children
    return <>{children}</>;
  }

  // If the user is not signed in, redirect to sign in
  return <Navigate to={redirectTo} replace />;
}

export default ProtectedRoute;
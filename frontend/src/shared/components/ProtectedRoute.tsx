import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/shared/hooks/useAuth'
import { Loading } from '@/shared/components/ui/loading'

interface ProtectedRouteProps {
  children: ReactNode
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoadingUser } = useAuth()
  const location = useLocation()

  // While determining auth state, show a lightweight loading UI
  if (isLoadingUser) {
    return <Loading message="Checking authentication..." />
  }

  // If not authenticated, redirect to /auth and keep the intended destination
  if (!isAuthenticated) {
    return <Navigate to="/auth" state={{ from: location }} replace />
  }

  // Otherwise render the protected content
  return <>{children}</>
}

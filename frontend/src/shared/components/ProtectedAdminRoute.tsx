import { Navigate } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'

interface ProtectedAdminRouteProps {
  children: React.ReactNode
}

export function ProtectedAdminRoute({ children }: ProtectedAdminRouteProps) {
  const { isSignedIn, isLoaded } = useAuth();

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!isSignedIn) {
    return <Navigate to="/auth/sign-in" replace />
  }

  // For now, we'll assume all signed-in users are admins
  // In a real app, you'd check user.organizationMemberships or similar
  const isAdmin = true // TODO: Implement proper admin check

  if (!isAdmin) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

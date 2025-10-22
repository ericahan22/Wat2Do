import { Button } from '@/shared/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card'
import { Loading } from '@/shared/components/ui/loading'
import { useAuth } from '@/shared/hooks/useAuth'
import { useAuthRedirect } from '@/shared/hooks/useAuthRedirect'

export const Dashboard = () => {
  const { user, logout, isLoggingOut, isLoadingUser } = useAuth()
  useAuthRedirect() // Redirect to home if not authenticated

  if (isLoadingUser) {
    return <Loading message="Loading dashboard..." />
  }

  const handleLogout = () => {
    logout()
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-bold">Welcome to your Dashboard</CardTitle>
            <CardDescription>
              You are successfully authenticated!
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h3 className="text-lg font-semibold">User Information:</h3>
              <div className="bg-gray-100 p-4 rounded-lg">
                <p><strong>ID:</strong> {user?.id}</p>
                <p><strong>Email:</strong> {user?.email}</p>
              </div>
            </div>
            
            <Button 
              onClick={handleLogout} 
              className="w-full" 
              variant="destructive"
              disabled={isLoggingOut}
            >
              {isLoggingOut ? 'Logging out...' : 'Logout'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}


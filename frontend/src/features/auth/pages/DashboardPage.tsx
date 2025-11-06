import { Button } from '@/shared/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card'
import { Badge } from '@/shared/components/ui/badge'
import { useUser } from '@clerk/clerk-react'
import { useNavigate } from 'react-router-dom'
import { Plus, FileText, Calendar, User, Settings } from 'lucide-react'
import { useUserSubmissions } from '@/features/events/hooks/useUserSubmissions'
import type { EventSubmission } from '@/features/events/types/submission'
import { CLERK_ROUTES } from '@/shared/config/clerk'

export const DashboardPage = () => {
  const { user } = useUser()
  const navigate = useNavigate()

  // Fetch user's submissions
  const { data: submissions = [] } = useUserSubmissions()

  const pendingCount = submissions.filter((s: EventSubmission) => s.status === 'pending').length
  const approvedCount = submissions.filter((s: EventSubmission) => s.status === 'approved').length

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Welcome back, {user?.firstName || user?.username || 'User'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage your event submissions and activities
          </p>
        </div>

        {/* Workflow Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Submit Event Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/submit')}>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                  <Plus className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <CardTitle className="text-lg">Submit Event</CardTitle>
                  <CardDescription>Share an event with the community</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button className="w-full" variant="outline">
                Submit New Event
              </Button>
            </CardContent>
          </Card>

          {/* My Submissions Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/dashboard/submissions')}>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                  <FileText className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <CardTitle className="text-lg">My Submissions</CardTitle>
                  <CardDescription>Track your event submissions</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Pending</span>
                  <Badge variant="secondary">{pendingCount}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Approved</span>
                  <Badge variant="default">{approvedCount}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Browse Events Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/events')}>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                  <Calendar className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <CardTitle className="text-lg">Browse Events</CardTitle>
                  <CardDescription>Discover upcoming events</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button className="w-full" variant="outline">
                View Events
              </Button>
            </CardContent>
          </Card>

          {/* Profile Settings Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate(CLERK_ROUTES.USER_PROFILE)}>
            <CardHeader className="pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
                  <Settings className="h-6 w-6 text-orange-600 dark:text-orange-400" />
                </div>
                <div>
                  <CardTitle className="text-lg">Profile Settings</CardTitle>
                  <CardDescription>Manage your account</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button className="w-full" variant="outline">
                Edit Profile
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* User Info Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-gray-900 dark:text-gray-100">
              Account Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
              <div className="flex items-center gap-3 mb-3">
                <User className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                <span className="font-medium">User Details</span>
              </div>
              <p><strong>ID:</strong> {user?.id}</p>
              <p><strong>Email:</strong> {user?.primaryEmailAddress?.emailAddress}</p>
            </div>
         
          </CardContent>
        </Card>
      </div>
    </div>
  )
}


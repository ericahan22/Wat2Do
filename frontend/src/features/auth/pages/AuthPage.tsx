import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/components/ui/tabs'
import { LoginForm } from '@/features/auth/components/LoginForm'
import { SignupForm } from '@/features/auth/components/SignupForm'
import { SuccessMessage } from '@/features/auth/components/SuccessMessage'
import { useAuth } from '@/shared/hooks/useAuth'
import { AUTH_MESSAGES } from '@/features/auth/constants/auth'
import type { SignupRequest, AuthMutationOptions } from '@/features/auth/types/auth'

export const AuthPage = () => {
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login')
  const [signupSuccess, setSignupSuccess] = useState(false)
  
  const { login, signup, isLoggingIn, isSigningUp, loginError, signupError } = useAuth()

  const handleSignupSuccess = () => {
    setSignupSuccess(true)
  }

  const handleSignupSubmit = (data: SignupRequest, options?: AuthMutationOptions) => {
    signup(data, options)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center text-gray-900 dark:text-gray-100">Welcome</CardTitle>
          <CardDescription className="text-center">
            Sign in to your account or create a new one. Emails are encrypted.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'login' | 'signup')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>

            <TabsContent value="login" className="space-y-4">
              <LoginForm 
                onSubmit={login}
                isLoading={isLoggingIn}
                error={loginError}
              />
            </TabsContent>

            <TabsContent value="signup" className="space-y-4">
              {signupSuccess && (
                <SuccessMessage message={AUTH_MESSAGES.SIGNUP_SUCCESS} />
              )}
              <SignupForm 
                onSubmit={handleSignupSubmit}
                isLoading={isSigningUp}
                error={signupError}
                onSuccess={handleSignupSuccess}
              />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}


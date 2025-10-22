import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Label } from '@/shared/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/components/ui/tabs'
import { useAuth } from '@/shared/hooks/useAuth'
import { useGuestRedirect } from '@/shared/hooks/useAuthRedirect'
import { loginSchema, signupSchema, type LoginFormData, type SignupFormData } from '../schemas/authSchemas'

export const AuthPage = () => {
  useGuestRedirect() // Redirect to dashboard if already authenticated
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login')
  const [signupSuccess, setSignupSuccess] = useState(false)
  const { login, signup, isLoggingIn, isSigningUp, loginError, signupError } = useAuth()

  const loginForm = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  })

  const signupForm = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
    },
  })

  const onLoginSubmit = (data: LoginFormData) => {
    login(data)
  }

  const onSignupSubmit = (data: SignupFormData) => {
    const { confirmPassword: _, ...signupData } = data
    signup(signupData, {
      onSuccess: () => {
        setSignupSuccess(true)
        signupForm.reset()
      }
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Welcome</CardTitle>
          <CardDescription className="text-center">
            Sign in to your account or create a new one 
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'login' | 'signup')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>

            <TabsContent value="login" className="space-y-4">
              <form onSubmit={loginForm.handleSubmit(onLoginSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="login-email">Email</Label>
                  <Input
                    id="login-email"
                    type="email"
                    placeholder="Enter your email"
                    {...loginForm.register('email')}
                  />
                  {loginForm.formState.errors.email && (
                    <p className="text-sm text-red-600">{loginForm.formState.errors.email.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="login-password">Password</Label>
                  <Input
                    id="login-password"
                    type="password"
                    placeholder="Enter your password"
                    {...loginForm.register('password')}
                  />
                  {loginForm.formState.errors.password && (
                    <p className="text-sm text-red-600">{loginForm.formState.errors.password.message}</p>
                  )}
                </div>

                {loginError && (
                  <p className="text-sm text-red-600">{loginError.message}</p>
                )}

                <Button type="submit" className="w-full" disabled={isLoggingIn}>
                  {isLoggingIn ? 'Signing in...' : 'Sign In'}
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="signup" className="space-y-4">
              {signupSuccess && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-sm text-green-800">
                    ✅ Successfully sent confirmation email! Please check your inbox.
                  </p>
                </div>
              )}
              <form onSubmit={signupForm.handleSubmit(onSignupSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="signup-email">Email</Label>
                  <Input
                    id="signup-email"
                    type="email"
                    placeholder="Enter your email"
                    {...signupForm.register('email')}
                  />
                  {signupForm.formState.errors.email && (
                    <p className="text-sm text-red-600">{signupForm.formState.errors.email.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="signup-password">Password</Label>
                  <Input
                    id="signup-password"
                    type="password"
                    placeholder="Enter your password"
                    {...signupForm.register('password')}
                  />
                  {signupForm.formState.errors.password && (
                    <p className="text-sm text-red-600">{signupForm.formState.errors.password.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="signup-confirm-password">Confirm Password</Label>
                  <Input
                    id="signup-confirm-password"
                    type="password"
                    placeholder="Confirm your password"
                    {...signupForm.register('confirmPassword')}
                  />
                  {signupForm.formState.errors.confirmPassword && (
                    <p className="text-sm text-red-600">{signupForm.formState.errors.confirmPassword.message}</p>
                  )}
                </div>

                {signupError && (
                  <p className="text-sm text-red-600">{signupError.message}</p>
                )}

                <Button type="submit" className="w-full" disabled={isSigningUp}>
                  {isSigningUp ? 'Creating account...' : 'Create Account'}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}


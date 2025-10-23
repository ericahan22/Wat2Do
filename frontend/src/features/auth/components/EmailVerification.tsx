import { useSearchParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Button } from '@/shared/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card'
import { useAuth } from '@/shared/hooks/useAuth'

export const EmailVerification = () => {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const { confirmEmail, isConfirmingEmail, confirmEmailError } = useAuth()
  const [verificationStatus, setVerificationStatus] = useState<'pending' | 'success' | 'error'>('pending')

  useEffect(() => {
    if (token) {
      confirmEmail(token, {
        onSuccess: () => setVerificationStatus('success'),
        onError: () => setVerificationStatus('error'),
      })
    }
  }, [token, confirmEmail])

  const handleManualConfirm = () => {
    if (token) {
      confirmEmail(token, {
        onSuccess: () => setVerificationStatus('success'),
        onError: () => setVerificationStatus('error'),
      })
    }
  }

  if (verificationStatus === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-green-600">Email Verified!</CardTitle>
            <CardDescription>
              Your email has been successfully verified. You can now access your dashboard.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => window.location.href = '/dashboard'} 
              className="w-full"
            >
              Go to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (verificationStatus === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-red-600">Verification Failed</CardTitle>
            <CardDescription>
              {confirmEmailError?.message || 'There was an error verifying your email. Please try again.'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={handleManualConfirm} 
              className="w-full"
              disabled={isConfirmingEmail}
            >
              {isConfirmingEmail ? 'Verifying...' : 'Try Again'}
            </Button>
            <Button 
              variant="outline" 
              onClick={() => window.location.href = '/auth'} 
              className="w-full"
            >
              Back to Login
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Check Your Email</CardTitle>
          <CardDescription>
            We've sent you a verification link. Please check your inbox and click the link to verify your email address.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center text-sm text-gray-600">
            <p>If you don't see the email, check your spam folder.</p>
            <p>Click the button below to manually verify your email:</p>
          </div>
          
          {token && (
            <Button 
              onClick={handleManualConfirm} 
              className="w-full"
              disabled={isConfirmingEmail}
            >
              {isConfirmingEmail ? 'Verifying...' : 'Verify Email'}
            </Button>
          )}
          
          <Button 
            variant="outline" 
            onClick={() => window.location.href = '/auth'} 
            className="w-full"
          >
            Back to Login
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}


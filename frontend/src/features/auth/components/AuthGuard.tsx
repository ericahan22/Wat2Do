import { useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Button } from '@/shared/components/ui/button';
import { Alert, AlertDescription } from '@/shared/components/ui';
import { Mail, RefreshCw } from 'lucide-react';
import { useAuth } from '@/shared/hooks';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
  requireEmailVerification?: boolean;
}

export function AuthGuard({ 
  children, 
  requireAdmin = false, 
  requireEmailVerification = true 
}: AuthGuardProps) {
  const [isResending, setIsResending] = useState(false);
  const [resendMessage, setResendMessage] = useState('');
  const location = useLocation();

  const { isAuthenticated, isLoading, emailVerified, isAdmin, email, refreshAuth, resendVerification } = useAuth();

  const handleResendVerification = async () => {
    if (!email) return;
    
    setIsResending(true);
    setResendMessage('');

    try {
      await resendVerification(email);
      setResendMessage('Verification email sent! Please check your inbox.');
    } catch (err) {
      setResendMessage('Failed to send verification email. Please try again.');
    } finally {
      setIsResending(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireAdmin && !isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600">
            You need admin privileges to access this page.
          </p>
        </div>
      </div>
    );
  }

  if (requireEmailVerification && !emailVerified) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
              Email Verification Required
            </h2>
          </div>
          
          <Card>
            <CardHeader>
              <div className="flex justify-center mb-4">
                <Mail className="h-16 w-16 text-blue-600" />
              </div>
              <CardTitle className="text-center">Verify Your Email</CardTitle>
              <CardDescription className="text-center">
                Please check your UWaterloo email and click the verification link to access this feature.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <AlertDescription>
                  We've sent a verification email to your UWaterloo email address. 
                  Please check your inbox and click the verification link.
                </AlertDescription>
              </Alert>

              {resendMessage && (
                <Alert variant={resendMessage.includes('sent') ? 'default' : 'destructive'}>
                  <AlertDescription>{resendMessage}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Button 
                  onClick={handleResendVerification} 
                  disabled={isResending}
                  className="w-full"
                >
                  {isResending ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    'Resend Verification Email'
                  )}
                </Button>
                
                <Button 
                  variant="outline" 
                  onClick={refreshAuth}
                  className="w-full"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Check Verification Status
                </Button>
                
                <Button 
                  variant="outline" 
                  onClick={() => window.location.href = '/login'}
                  className="w-full"
                >
                  Back to Login
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

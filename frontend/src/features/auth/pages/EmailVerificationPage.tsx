import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Button } from '@/shared/components/ui/button';
import { Alert, AlertDescription } from '@/shared/components/ui';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { API_BASE_URL } from '@/shared/constants/api';

export function EmailVerificationPage() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setError('No verification token provided');
      return;
    }

    verifyEmail(token);
  }, [token]);

  const verifyEmail = async (verificationToken: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/verify-email/${verificationToken}/`);

      const data = await response.json();

      if (response.ok) {
        setStatus('success');
        setMessage(data.message || 'Email verified successfully!');
      } else {
        setStatus('error');
        setError(data.error || 'Failed to verify email');
      }
    } catch (err) {
      setStatus('error');
      setError('Network error. Please try again.');
    }
  };

  const handleGoToLogin = () => {
    navigate('/login');
  };

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Email Verification
          </h2>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-center">
              {status === 'loading' && 'Verifying your email...'}
              {status === 'success' && 'Email Verified!'}
              {status === 'error' && 'Verification Failed'}
            </CardTitle>
            <CardDescription className="text-center">
              {status === 'loading' && 'Please wait while we verify your email address.'}
              {status === 'success' && 'Your email has been successfully verified.'}
              {status === 'error' && 'There was a problem verifying your email.'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {status === 'loading' && (
              <div className="flex justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              </div>
            )}

            {status === 'success' && (
              <>
                <div className="flex justify-center">
                  <CheckCircle className="h-16 w-16 text-green-600" />
                </div>
                <Alert>
                  <AlertDescription>{message}</AlertDescription>
                </Alert>
                <div className="flex flex-col gap-2">
                  <Button onClick={handleGoToLogin} className="w-full">
                    Go to Login
                  </Button>
                  <Button variant="outline" onClick={handleGoHome} className="w-full">
                    Go to Home
                  </Button>
                </div>
              </>
            )}

            {status === 'error' && (
              <>
                <div className="flex justify-center">
                  <XCircle className="h-16 w-16 text-red-600" />
                </div>
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
                <div className="flex flex-col gap-2">
                  <Button onClick={handleGoToLogin} className="w-full">
                    Go to Login
                  </Button>
                  <Button variant="outline" onClick={handleGoHome} className="w-full">
                    Go to Home
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

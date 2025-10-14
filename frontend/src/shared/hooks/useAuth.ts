import { useState, useEffect } from 'react';
import { apiRequest, API_ENDPOINTS } from '@/shared/lib/api';

interface AuthUser {
  email: string;
  is_admin: boolean;
  email_verified: boolean;
}

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkAuthStatus = async () => {
    try {
      const response = await apiRequest(API_ENDPOINTS.AUTH.STATUS);
      
      if (response.ok) {
        const data = await response.json();
        setIsAuthenticated(true);
        setUser({
          email: data.email,
          is_admin: data.is_admin,
          email_verified: data.email_verified,
        });
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (err) {
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiRequest(API_ENDPOINTS.AUTH.LOGIN, {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Login failed');
      }

      const data = await response.json();
      
      // Update auth state
      setIsAuthenticated(true);
      setUser({
        email: data.email,
        is_admin: data.is_admin,
        email_verified: data.email_verified,
      });
      
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (password: string, email: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiRequest(API_ENDPOINTS.AUTH.REGISTER, {
        method: 'POST',
        body: JSON.stringify({ password, email }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Registration failed');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Registration failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiRequest(API_ENDPOINTS.AUTH.LOGOUT, {
        method: 'POST',
      });
    } catch (err) {
      // Ignore logout errors
    } finally {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const resendVerification = async (email: string) => {
    try {
      const response = await apiRequest(API_ENDPOINTS.AUTH.RESEND_VERIFICATION, {
        method: 'POST',
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to resend verification');
      }

      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to resend verification';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  };

  // Check auth status on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  return {
    isAuthenticated,
    isLoading,
    emailVerified: user?.email_verified ?? false,
    isAdmin: user?.is_admin ?? false,
    email: user?.email ?? null,
    user,
    login,
    register,
    logout,
    resendVerification,
    refreshAuth: checkAuthStatus,
    error,
  };
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from '@/shared/stores/authStore'
import { authAPIClient, type SignupRequest, type LoginRequest } from '@/shared/api'
import { AUTH_ROUTES } from '@/features/auth/constants/auth'
import type { AuthMutationOptions } from '@/features/auth/types/auth'

export const useAuth = () => {
  const { user, isAuthenticated, setUser, logout: logoutStore } = useAuthStore()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: currentUser, isLoading: isLoadingUser, error: currentUserError } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => authAPIClient.getCurrentUser(),
    enabled: isAuthenticated,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes - auth state doesn't change often
    gcTime: 10 * 60 * 1000, // 10 minutes
  })

  // Handle authentication errors
  useEffect(() => {
    if (currentUserError) {
      const error = currentUserError 
      if (error) {
        logoutStore()
        queryClient.removeQueries({ queryKey: ['auth'], exact: false })
      }
    }
  }, [currentUserError, logoutStore, queryClient])

  if (currentUser && currentUser.id !== user?.id) {
    setUser(currentUser)
  }

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginRequest) => authAPIClient.login(credentials),
    onSuccess: (data) => {
      if (data.user) {
        setUser(data.user)
        // Don't invalidate queries - we already have the user data from login response
        // Navigation removed - let components handle their own navigation
      }
    },
  })

  // Signup mutation
  const signupMutation = useMutation({
    mutationFn: (userData: SignupRequest) => authAPIClient.signup(userData),
    onSuccess: (data) => {
      if (data.user) {
        setUser(data.user)
        queryClient.invalidateQueries({ queryKey: ['auth'] })
      }
    },
  })

  const login = (credentials: LoginRequest, options?: AuthMutationOptions) => {
    loginMutation.mutate(credentials, {
      onSuccess: () => {
        options?.onSuccess?.()
        navigate(AUTH_ROUTES.DASHBOARD)
      },
      onError: (error) => {
        options?.onError?.(error)
      },
    })
  }

  const signup = (data: SignupRequest, options?: AuthMutationOptions) => {
    signupMutation.mutate(data, {
      onSuccess: (response) => {
        if (response.user) {
          setUser(response.user)
          queryClient.invalidateQueries({ queryKey: ['auth'] })
          navigate(AUTH_ROUTES.VERIFY_EMAIL)
        }
        options?.onSuccess?.()
      },
      onError: (error) => {
        options?.onError?.(error)
      },
    })
  }

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: () => authAPIClient.logout(),
    onSuccess: () => {
      logoutStore()
      // Remove only auth- and admin-scoped data
      queryClient.removeQueries({ queryKey: ['auth'], exact: false })
      queryClient.removeQueries({ queryKey: ['admin'], exact: false })
      navigate('/')
    },
  })

  // Confirm email mutation
  const confirmEmailMutation = useMutation({
    mutationFn: (token: string) => authAPIClient.confirmEmail(token),
    onSuccess: (data) => {
      if (data.user) {
        setUser(data.user)
        queryClient.invalidateQueries({ queryKey: ['auth'] })
        navigate('/dashboard')
      }
    },
  })

  const _confirmEmail = (token: string, options?: { onSuccess?: () => void; onError?: () => void }) => {
    confirmEmailMutation.mutate(token, {
      onSuccess: (data) => {
        if (data.user) {
          setUser(data.user)
          queryClient.invalidateQueries({ queryKey: ['auth'] })
          navigate('/dashboard')
        }
        options?.onSuccess?.()
      },
      onError: () => {
        options?.onError?.()
      },
    })
  }

  return {
    user,
    isAuthenticated,
    isAdmin: user?.is_staff || user?.is_superuser || false,
    isLoadingUser,
    login,
    signup,
    logout: logoutMutation.mutate,
    confirmEmail: _confirmEmail,
    isLoggingIn: loginMutation.isPending,
    isSigningUp: signupMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    isConfirmingEmail: confirmEmailMutation.isPending,
    loginError: loginMutation.error,
    signupError: signupMutation.error,
    logoutError: logoutMutation.error,
    confirmEmailError: confirmEmailMutation.error,
  }
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from '../stores/authStore'
import { authApi, type SignupRequest } from '../api/auth'

export const useAuth = () => {
  const { user, isAuthenticated, setUser, logout: logoutStore } = useAuthStore()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Get current user query
  const { data: currentUser, isLoading: isLoadingUser, error: currentUserError } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticated,
    retry: false,
  })

  // Handle authentication errors
  useEffect(() => {
    if (currentUserError) {
      const error = currentUserError 
      if (error) {
        logoutStore()
        queryClient.clear()
      }
    }
  }, [currentUserError, logoutStore, queryClient])

  // Update store when user data changes
  if (currentUser && currentUser.id !== user?.id) {
    setUser(currentUser)
  }

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      if (data.user) {
        setUser(data.user)
        queryClient.invalidateQueries({ queryKey: ['auth'] })
        navigate('/dashboard')
      }
    },
  })

  // Signup mutation
  const signupMutation = useMutation({
    mutationFn: authApi.signup,
    onSuccess: (data) => {
      if (data.user) {
        setUser(data.user)
        queryClient.invalidateQueries({ queryKey: ['auth'] })
        navigate('/auth/verify-email')
      }
    },
  })

  const signup = (data: SignupRequest, options?: { onSuccess?: () => void; onError?: () => void }) => {
    signupMutation.mutate(data, {
      onSuccess: (response) => {
        if (response.user) {
          setUser(response.user)
          queryClient.invalidateQueries({ queryKey: ['auth'] })
          navigate('/auth/verify-email')
        }
        options?.onSuccess?.()
      },
      onError: () => {
        options?.onError?.()
      },
    })
  }

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: authApi.logout,
    onSuccess: () => {
      logoutStore()
      queryClient.clear()
      navigate('/')
    },
  })

  // Confirm email mutation
  const confirmEmailMutation = useMutation({
    mutationFn: authApi.confirmEmail,
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
    isLoadingUser,
    login: loginMutation.mutate,
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

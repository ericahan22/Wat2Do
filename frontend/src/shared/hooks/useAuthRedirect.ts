import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from './useAuth'

export const useAuthRedirect = (redirectTo: string = '/') => {
  const { isAuthenticated, isLoadingUser } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoadingUser && !isAuthenticated) {
      navigate(redirectTo)
    }
  }, [isAuthenticated, isLoadingUser, navigate, redirectTo])

  return { isAuthenticated, isLoadingUser }
}

export const useGuestRedirect = (redirectTo: string = '/dashboard') => {
  const { isAuthenticated, isLoadingUser } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoadingUser && isAuthenticated) {
      navigate(redirectTo)
    }
  }, [isAuthenticated, isLoadingUser, navigate, redirectTo])

  return { isAuthenticated, isLoadingUser }
}


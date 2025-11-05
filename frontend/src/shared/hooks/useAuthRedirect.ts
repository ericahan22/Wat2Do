import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'

export const useAuthRedirect = (redirectTo: string = '/auth') => {
  const { isSignedIn, isLoaded } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      navigate(redirectTo)
    }
  }, [isSignedIn, isLoaded, navigate, redirectTo])

  return { isSignedIn, isLoaded }
}

export const useGuestRedirect = (redirectTo: string = '/dashboard') => {
  const { isSignedIn, isLoaded } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isLoaded && isSignedIn) {
      navigate(redirectTo)
    }
  }, [isSignedIn, isLoaded, navigate, redirectTo])

  return { isSignedIn, isLoaded }
}
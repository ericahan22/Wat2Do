import { AuthForm } from '../components/AuthForm'
import { useGuestRedirect } from '@/shared/hooks/useAuthRedirect'

export const AuthPage = () => {
  useGuestRedirect() // Redirect to dashboard if already authenticated

  return <AuthForm />
}


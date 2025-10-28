// Components
export { LoginForm } from './components/LoginForm';
export { SignupForm } from './components/SignupForm';
export { SuccessMessage } from './components/SuccessMessage';

// Types
export type {
  User,
  LoginRequest,
  SignupRequest,
  AuthResponse,
  AuthError,
  AuthFormData,
  SignupFormData,
  LoginFormData,
  AuthMutationOptions,
} from './types/auth';

// Constants
export { AUTH_ROUTES, AUTH_MESSAGES, AUTH_FORM_LABELS, AUTH_FORM_PLACEHOLDERS } from './constants/auth';

// Schemas
export { loginSchema, signupSchema } from './schemas/authSchemas';
export type { LoginFormData as LoginFormDataSchema, SignupFormData as SignupFormDataSchema } from './schemas/authSchemas';

// Pages
export { AuthPage } from './pages/AuthPage';
export { VerifyEmailPage } from './pages/VerifyEmailPage';
export { DashboardPage } from './pages/DashboardPage';
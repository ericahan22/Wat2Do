export const AUTH_ROUTES = {
  LOGIN: '/auth',
  SIGNUP: '/auth',
  VERIFY_EMAIL: '/auth/verify-email',
  DASHBOARD: '/dashboard',
  HOME: '/',
} as const;

export const AUTH_MESSAGES = {
  LOGIN_SUCCESS: 'Successfully logged in!',
  SIGNUP_SUCCESS: 'Successfully sent confirmation email! Please check your inbox.',
  LOGOUT_SUCCESS: 'Successfully logged out!',
  EMAIL_VERIFIED: 'Email verified successfully!',
  INVALID_CREDENTIALS: 'Invalid email or password',
  EMAIL_ALREADY_EXISTS: 'Email already exists',
  NETWORK_ERROR: 'Network error. Please try again.',
} as const;

export const AUTH_FORM_LABELS = {
  EMAIL: 'Email',
  PASSWORD: 'Password',
  CONFIRM_PASSWORD: 'Confirm Password',
  SIGN_IN: 'Sign In',
  CREATE_ACCOUNT: 'Create Account',
  SIGNING_IN: 'Signing in...',
  CREATING_ACCOUNT: 'Creating account...',
} as const;

export const AUTH_FORM_PLACEHOLDERS = {
  EMAIL: 'Enter your email',
  PASSWORD: 'Enter your password',
  CONFIRM_PASSWORD: 'Confirm your password',
} as const;

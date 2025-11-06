/**
 * Clerk Configuration
 * Centralized configuration for Clerk authentication
 */

export const CLERK_CONFIG = {
  publishableKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY,
  signInUrl: '/auth/sign-in',
  signUpUrl: '/auth/sign-up',
  afterSignInUrl: '/dashboard',
  afterSignUpUrl: '/auth/verify-email',
  afterSignOutUrl: '/',
} as const;

export const CLERK_ROUTES = {
  SIGN_IN: '/auth/sign-in',
  SIGN_UP: '/auth/sign-up',
  VERIFY_EMAIL: '/auth/verify-email',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  USER_PROFILE: '/user-profile',
  DASHBOARD: '/dashboard',
  HOME: '/',
} as const;

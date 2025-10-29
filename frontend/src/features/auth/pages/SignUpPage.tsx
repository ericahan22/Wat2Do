/**
 * Sign Up Page
 * Clerk-powered sign up page
 */

import { SignUp } from '@clerk/clerk-react';
import { AuthGuard } from '@/shared/components/AuthGuard';
import { CLERK_ROUTES } from '@/shared/config/clerk';

export const SignUpPage = () => {
  return (
    <AuthGuard requireGuest>
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
              Create your account
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
              Or{' '}
              <a
                href={CLERK_ROUTES.SIGN_IN}
                className="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400"
              >
                sign in to your existing account
              </a>
            </p>
          </div>
          <div className="flex justify-center">
            <SignUp 
              appearance={{
                elements: {
                  formButtonPrimary: 'bg-indigo-600 hover:bg-indigo-700 text-white',
                  card: 'shadow-lg',
                },
              }}
            />
          </div>
        </div>
      </div>
    </AuthGuard>
  );
};

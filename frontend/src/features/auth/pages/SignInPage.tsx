/**
 * Sign In Page
 * Clerk-powered sign in page
 */

import { SignIn } from "@clerk/clerk-react";
import { AuthGuard } from "@/shared/components/AuthGuard";
import { CLERK_ROUTES } from "@/shared/config/clerk";

export const SignInPage = () => {
  return (
    <AuthGuard requireGuest>
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <SignIn
          signUpUrl={CLERK_ROUTES.SIGN_UP}
          appearance={{
            elements: {
              formButtonPrimary: "bg-indigo-600 hover:bg-indigo-700 text-white",
              card: "shadow-lg",
            },
          }}
        />
      </div>
    </AuthGuard>
  );
};

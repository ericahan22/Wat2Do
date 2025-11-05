import { SignUp } from "@clerk/clerk-react";
import { AuthGuard } from "@/shared/components/AuthGuard";

export const SignUpPage = () => {
  return (
    <AuthGuard requireGuest>
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <SignUp
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

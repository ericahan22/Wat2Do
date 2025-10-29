// src/pages/SignUpPage.jsx
import { SignUp } from '@clerk/clerk-react';

function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <div className="flex justify-center">
          <SignUp 
            appearance={{
              elements: {
                formButtonPrimary: "bg-blue-600 hover:bg-blue-700 text-sm normal-case",
                card: "shadow-lg",
                headerTitle: "text-gray-900",
                headerSubtitle: "text-gray-600",
                socialButtonsBlockButton: "border border-gray-300 hover:bg-gray-50",
                formFieldInput: "border border-gray-300 focus:border-blue-500 focus:ring-blue-500",
                footerActionLink: "text-blue-600 hover:text-blue-500"
              }
            }}
            routing="path"
            path="/auth/sign-up"
            signInUrl="/auth/sign-in"
          />
        </div>
      </div>
    </div>
  );
}

export default SignUpPage;

/**
 * User Profile Page
 * Clerk's pre-built UserProfile component for managing account settings
 */

import { UserProfile } from "@clerk/clerk-react";
import { dark } from "@clerk/themes";
import { useTheme } from "@/shared/hooks/useTheme";

export const UserProfilePage = () => {
  const { theme } = useTheme();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <UserProfile
        appearance={{
          baseTheme: theme === 'dark' ? dark : undefined,
          elements: {
            rootBox: "mx-auto",
            card: "shadow-xl",
          },
        }}
        routing="path"
        path="/user-profile"
      />
    </div>
  );
};


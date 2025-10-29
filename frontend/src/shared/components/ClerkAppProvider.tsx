/**
 * Clerk Provider Component
 * Wraps the app with Clerk authentication provider
 */

import { ClerkProvider } from "@clerk/clerk-react";
import { CLERK_CONFIG } from "@/shared/config/clerk";
import { dark } from "@clerk/themes";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@/shared/hooks/useTheme";

interface ClerkAppProviderProps {
  children: React.ReactNode;
}

export const ClerkAppProvider = ({ children }: ClerkAppProviderProps) => {
  if (!CLERK_CONFIG.publishableKey) {
    throw new Error("VITE_CLERK_PUBLISHABLE_KEY is required");
  }
  const { theme } = useTheme();

  const navigate = useNavigate();

  return (
    <ClerkProvider
      publishableKey={CLERK_CONFIG.publishableKey}
      signInUrl={CLERK_CONFIG.signInUrl}
      signUpUrl={CLERK_CONFIG.signUpUrl}
      afterSignOutUrl={CLERK_CONFIG.afterSignOutUrl}
      routerPush={(to) => navigate(to)}
      routerReplace={(to) => navigate(to, { replace: true })}
      appearance={{
        baseTheme: theme === 'dark' ? dark : undefined,
      }}
    >
      {children}
    </ClerkProvider>
  );
};

import { useUser, useSession } from "@clerk/clerk-react";
import { useEffect, useState } from "react";

/**
 * Hook to check if the current user is an admin.
 * 
 * NOTE: This hook checks publicMetadata.role. If you're using privateMetadata
 * in Clerk, you need to either:
 * 1. Use publicMetadata instead (recommended for role)
 * 2. Configure Clerk to include privateMetadata in JWT tokens
 * 
 * After updating metadata in Clerk, call session.reload() to refresh the token.
 */
export function useAdmin() {
  const { user } = useUser();
  const { session } = useSession();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Check publicMetadata (privateMetadata is not accessible on frontend)
    const adminStatus = user?.publicMetadata?.role === 'admin';
    setIsAdmin(adminStatus);

    // If metadata was just updated, reload session to get fresh token
    // This is especially important in production where tokens refresh every ~60s
    if (user && session && !adminStatus && user.publicMetadata) {
      // Check if we should reload (e.g., after a metadata update)
      // This is a safety mechanism - in practice, you should call session.reload()
      // explicitly after updating metadata
    }
  }, [user, session]);

  /**
   * Force refresh the session token to pick up metadata changes.
   * Call this after updating user metadata in Clerk.
   */
  const refreshSession = async () => {
    if (session) {
      await session.reload();
    }
  };

  return { isAdmin, refreshSession };
}





import { useUser } from "@clerk/clerk-react";

export function useAdmin() {
  const { user } = useUser();
  const isAdmin = user?.publicMetadata?.role === 'admin';
  
  return { isAdmin };
}


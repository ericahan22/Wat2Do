import { useQuery } from '@tanstack/react-query';
import { useApi } from '@/shared/hooks/useApi';
import { useAuth } from '@clerk/clerk-react';

export const useUserSubmissions = () => {
  const { isSignedIn, userId } = useAuth();
  const { events } = useApi();

  return useQuery({
    queryKey: ['user-submissions', userId],
    queryFn: () => events.getUserSubmissions(),
    enabled: isSignedIn && !!userId,
    staleTime: 30 * 1000, // 30 seconds - submissions don't change often
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
};

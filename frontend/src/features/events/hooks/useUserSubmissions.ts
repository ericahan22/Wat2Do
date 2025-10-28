import { useQuery } from '@tanstack/react-query';
import { eventsAPIClient } from '@/shared/api';

export const useUserSubmissions = () => {
  return useQuery({
    queryKey: ['user-submissions'],
    queryFn: eventsAPIClient.getUserSubmissions,
    staleTime: 30 * 1000, // 30 seconds - submissions don't change often
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
};

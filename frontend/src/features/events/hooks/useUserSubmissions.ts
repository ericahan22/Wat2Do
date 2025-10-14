import { useQuery } from '@tanstack/react-query';
import { apiRequest } from '@/shared/lib/api';
import { SubmittedEvent } from '../types/events';

export function useUserSubmissions() {
  const query = useQuery({
    queryKey: ['userSubmissions'],
    queryFn: async (): Promise<SubmittedEvent[]> => {
      const response = await apiRequest('/events/submissions/');

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch submissions');
      }

      return response.json();
    },
  });

  return {
    submissions: query.data || [],
    isLoading: query.isLoading,
    error: query.error?.message || null,
    refetch: query.refetch,
  };
}

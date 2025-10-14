import { useQuery } from '@tanstack/react-query';
import { useLocalStorage } from 'react-use';
import { SubmittedClub } from '../types/clubs';
import { API_BASE_URL } from '@/shared/constants/api';

export function useUserClubSubmissions() {
  const [authToken] = useLocalStorage<string>('authToken');

  const query = useQuery({
    queryKey: ['userClubSubmissions'],
    queryFn: async (): Promise<SubmittedClub[]> => {
      if (!authToken) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${API_BASE_URL}/clubs/submissions/`, {
        headers: {
          'Authorization': `Token ${authToken}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch club submissions');
      }

      return response.json();
    },
    enabled: !!authToken,
  });

  return {
    submissions: query.data || [],
    isLoading: query.isLoading,
    error: query.error?.message || null,
    refetch: query.refetch,
  };
}
